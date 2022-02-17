import json
import os
import random
import time
import uuid
from collections import defaultdict

import dotenv
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import (
    ApplicationCreateObject,
)
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials


def luis_add_app(client, appName, luis_version_id, luis_intent_name):
    appDefinition = ApplicationCreateObject(
        name=appName, initial_version_id=luis_version_id, culture="en-us"
    )
    luis_api_id = client.apps.add(appDefinition)

    # Add intention
    client.model.add_intent(luis_api_id, luis_version_id, luis_intent_name)

    print("Created LUIS app with ID {}".format(luis_api_id))
    return luis_api_id


def make_utterances_train(frames, intent_name):
    entities_g = defaultdict(int)
    for frame in frames:
        turn = frame["turns"][0]

        assert turn["author"] == "user"
        assert list(turn["labels"].keys()) == [
            "acts",
            "acts_without_refs",
            "active_frame",
            "frames",
        ]

        entities = {}
        for act in turn["labels"]["acts"]:
            if act["name"] == "inform":
                for arg in act["args"]:
                    entities[arg["key"]] = arg["val"]

        for k in entities:
            entities_g[k] += 1

    # We take entities with at least 50 occurances
    entities_g = list(filter(lambda x: entities_g[x] > 50, entities_g))
    entities_g.remove("intent")
    print(f"Entities detected from data : {entities_g}")

    # Create utteraces list
    utterance_list = []
    for frame in frames:
        turn = frame["turns"][0]
        entities = {}
        for act in turn["labels"]["acts"]:
            if act["name"] == "inform":
                for arg in act["args"]:
                    entities[arg["key"]] = arg["val"]

        if "intent" in entities:
            entities.pop("intent")

        labels = []
        for k in entities:
            if k in entities_g:
                v = str(entities[k])
                pos = turn["text"].find(v)
                if pos >= 0:
                    labels.append(
                        {
                            "startCharIndex": pos,
                            "endCharIndex": pos + len(v),
                            "entityName": k,
                        }
                    )
        if len(labels) > 0:
            utterance = {"text": turn["text"]}
            utterance["intentName"] = intent_name
            utterance["entityLabels"] = labels
            utterance_list.append(utterance)
    print(f"\nThere are {len(utterance_list)} utterances for intent {intent_name}")

    return entities_g, utterance_list


def make_utterances_test(frames, intent_name, entities_g):
    # Create utteraces list
    utterance_list = []
    for frame in frames:
        turn = frame["turns"][0]
        entities = {}
        for act in turn["labels"]["acts"]:
            if act["name"] == "inform":
                for arg in act["args"]:
                    entities[arg["key"]] = arg["val"]

        if "intent" in entities:
            entities.pop("intent")

        labels = []
        for k in entities:
            if k in entities_g:
                v = str(entities[k])
                pos = turn["text"].find(v)
                if pos >= 0:
                    labels.append(
                        {
                            "entity": k,
                            "startPos": pos,
                            "endPos": pos + len(v),
                        }
                    )
        if len(labels) > 0:
            utterance = {"text": turn["text"]}
            utterance["intent"] = intent_name
            utterance["entities"] = labels
            utterance_list.append(utterance)
    print(f"\nThere are {len(utterance_list)} utterances for intent {intent_name}")

    return utterance_list


def train_LUIS_model(
    utterance_train,
    client,
    luis_api_id,
    luis_version_id,
):

    for utterance in utterance_train:
        try:
            client.examples.add(
                luis_api_id,
                luis_version_id,
                utterance,
                # {"enableNestedChildren": False},
            )
        except:
            print(f"Failed to add : {utterance}")

    # client.examples.batch(
    #     luis_api_id,
    #     luis_version_id,
    #     utterance_train
    # )

    client.train.train_version(luis_api_id, luis_version_id)
    waiting = True
    while waiting:
        info = client.train.get_status(luis_api_id, luis_version_id)

        # get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
        waiting = any(
            map(
                lambda x: "Queued" == x.details.status
                or "InProgress" == x.details.status,
                info,
            )
        )
        if waiting:
            print("Waiting 10 seconds for training to complete...")
            time.sleep(10)
        else:
            print("trained")
            waiting = False

    # Mark the app as public so we can query it using any prediction endpoint.
    client.apps.update_settings(luis_api_id, is_public=True)

    client.apps.publish(luis_api_id, luis_version_id, is_staging=False)


if __name__ == "__main__":

    dotenv.load_dotenv()

    DATA_PATH = "./frames/"
    LUIS_VERSION_ID = "0.1"
    LUIS_INTENT_NAME = "BookFlight"
    TEST_SIZE_PERC = 0.2

    LUIS_APP_ID = os.getenv("LUIS_APP_ID", "")
    LUIS_AUTHORING_KEY = os.getenv("LUIS_AUTHORING_KEY", "")
    LUIS_AUTHORING_END_POINT = os.getenv("LUIS_AUTHORING_END_POINT", "")
    LUIS_PREDICTION_KEY = os.getenv("LUIS_PREDICTION_KEY", "")
    LUIS_PREDICTION_END_POINT = os.getenv("LUIS_PREDICTION_END_POINT", "")

    # Set Luis client
    client = LUISAuthoringClient(
        LUIS_AUTHORING_END_POINT, CognitiveServicesCredentials(LUIS_AUTHORING_KEY)
    )

    if not LUIS_APP_ID:
        # We use a UUID to avoid name collisions.
        appName = "Fly Me " + str(uuid.uuid4())
        LUIS_APP_ID = luis_add_app(client, appName, LUIS_VERSION_ID, LUIS_INTENT_NAME)

    frames = json.load(open(DATA_PATH + "frames.json"))

    # Create data train and test
    random.shuffle(frames)
    test_length = int(TEST_SIZE_PERC * len(frames))
    frames_train = frames[:-test_length]
    frames_test = frames[-test_length:]
    print(f"train size : {len(frames_train)}")
    print(f"test size : {len(frames_test)}")

    entities, utterance_train = make_utterances_train(frames_train, LUIS_INTENT_NAME)
    utterance_test = make_utterances_test(frames_test, LUIS_INTENT_NAME, entities)

    # save utterance_test to evaluate model in luis page
    with open("utterance_test.json", "w") as outfile:
        json.dump(utterance_test, outfile)

    # Add entity to app
    print("")
    for ent in entities:
        modelId = client.model.add_entity(LUIS_APP_ID, LUIS_VERSION_ID, name=ent)
        print(f"Entity added : {ent} (id={modelId})")

    # train model
    train_LUIS_model(utterance_train, client, LUIS_APP_ID, LUIS_VERSION_ID)

    # runtimeCredentials = CognitiveServicesCredentials(LUIS_PREDICTION_KEY)
    # clientRuntime = LUISRuntimeClient(
    #     endpoint=LUIS_PREDICTION_END_POINT, credentials=runtimeCredentials
    # )
    # # AttributeError: 'PredictionOperations' object has no attribute 'get_slot_prediction'
    # predictionRequest = {"query": "I want to book a fly from Paris to Roma."}
    # predictionResponse = clientRuntime.prediction.get_slot_prediction(
    #     luis_api_id, "Production", predictionRequest
    # )
    # print("Top intent: {}".format(predictionResponse.prediction.top_intent))
    # print("Sentiment: {}".format(predictionResponse.prediction.sentiment))
    # print("Intents: ")
    # for intent in predictionResponse.prediction.intents:
    #     print("\t{}".format(json.dumps(intent)))
    # print("Entities: {}".format(predictionResponse.prediction.entities))
