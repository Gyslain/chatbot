#%%
import json
import random
import re
import time
import uuid
from collections import defaultdict
from functools import reduce

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import (
    ApplicationCreateObject,
)
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from dotenv import dotenv_values
from msrest.authentication import CognitiveServicesCredentials
from pandas.api.types import is_datetime64_any_dtype as is_datetime

#%%
matplotlib.rcParams["figure.figsize"] = (20, 10)
config = dotenv_values(".env")

#%%
DATA_PATH = "./frames/"
authoringKey = config["LUIS_AUTHORING_KEY"]
authoringEndpoint = config["LUIS_AUTHORING_END_POINT"]
predictionKey = config["LUIS_PREDICTION_KEY"]
predictionEndpoint = config["LUIS_PREDICTION_END_POINT"]

#%%
# We use a UUID to avoid name collisions.
appName = "Fly Me " + str(uuid.uuid4())
versionId = "0.2"
intentName = "BookFlight"

#%%
# TODO definir une classe
client = LUISAuthoringClient(
    authoringEndpoint, CognitiveServicesCredentials(authoringKey)
)

#%%
# define app basics
appDefinition = ApplicationCreateObject(
    name=appName, initial_version_id=versionId, culture="en-us"
)

# create app
app_id = client.apps.add(appDefinition)

# get app id - necessary for all other changes
print("Created LUIS app with ID {}".format(app_id))


#%%
client.model.add_intent(app_id, versionId, intentName)


#%%
frames = json.load(open(DATA_PATH + "frames.json"))
# frames = pd.DataFrame(frames)
# frames

#%%
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

entities_g

#%%
entities_g = list(filter(lambda x: entities_g[x] > 50, entities_g))
entities_g.remove("intent")
entities_g

#%%
# add entity to app
for ent in entities_g:
    modelId = client.model.add_entity(app_id, versionId, name=ent)
    print(modelId)


#%%
utterance_list = []
# entities = ["dst_city", "or_city", "budget", "str_date", "end_date"]

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
        utterance["intentName"] = intentName
        utterance["entityLabels"] = labels
        utterance_list.append(utterance)

utterance_list

#%%
random.shuffle(utterance_list)
utterance_train = utterance_list[:-10]
utterance_test = utterance_list[-10:]


# %%
for utterance in utterance_train:
    try:
        client.examples.add(
            app_id,
            versionId,
            utterance,
            # {"enableNestedChildren": False},
        )
    except:
        print(f"Failed to add : {utterance}")

#%%
client.train.train_version(app_id, versionId)
waiting = True
while waiting:
    info = client.train.get_status(app_id, versionId)

    # get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
    waiting = any(
        map(
            lambda x: "Queued" == x.details.status or "InProgress" == x.details.status,
            info,
        )
    )
    if waiting:
        print("Waiting 10 seconds for training to complete...")
        time.sleep(10)
    else:
        print("trained")
        waiting = False


#%%
# Mark the app as public so we can query it using any prediction endpoint.
# Note: For production scenarios, you should instead assign the app to your own LUIS prediction endpoint. See:
# https://docs.microsoft.com/en-gb/azure/cognitive-services/luis/luis-how-to-azure-subscription#assign-a-resource-to-an-app
client.apps.update_settings(app_id, is_public=True)

responseEndpointInfo = client.apps.publish(app_id, versionId, is_staging=False)

# %%
runtimeCredentials = CognitiveServicesCredentials(predictionKey)
clientRuntime = LUISRuntimeClient(
    endpoint=predictionEndpoint, credentials=runtimeCredentials
)

#%%
# Production == slot name
predictionRequest = {"query": "I want to book a fly from Paris to Roma."}

# TODO AttributeError: 'PredictionOperations' object has no attribute 'get_slot_prediction'
predictionResponse = clientRuntime.prediction.get_slot_prediction(
    app_id, "Production", predictionRequest
)
print("Top intent: {}".format(predictionResponse.prediction.top_intent))
print("Sentiment: {}".format(predictionResponse.prediction.sentiment))
print("Intents: ")

for intent in predictionResponse.prediction.intents:
    print("\t{}".format(json.dumps(intent)))
print("Entities: {}".format(predictionResponse.prediction.entities))

# %%
r = requests.get(
    "https://luisressource2.cognitiveservices.azure.com/luis/prediction/v3.0/apps/b1872a40-c654-43cb-9ce3-c31cfa9a91f8/slots/production/predict?verbose=true&show-all-intents=true&log=true&subscription-key=cced1802b9ba4474bb99dd742b40343d&query=paris%20to%20oslo"
)
r.text
