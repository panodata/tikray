# Collection-level "Tikray Collection Transformation" definition.
# Includes two Moksha/jq transformation rules for unwrapping and flattening.

from pprint import pprint

from tikray import CollectionTransformation, MokshaTransformation


def structure_unwrap_flatten():
    data_in = {
        "message-source": "community",
        "message-type": "mixed-pickles",
        "records": [
            {"nested-list": [{"foo": 1}, [{"foo": 2}, {"foo": 3}]]},
        ],
    }

    transformation = CollectionTransformation(
        pre=MokshaTransformation().jq(".records").jq('.[] |= (."nested-list" |= flatten)'),
    )

    # Transform data and dump to stdout.
    data_out = transformation.apply(data_in)
    pprint(data_out)


def structure_select_fields():
    data_in = [
        {
            "meta": {"id": "Hotzenplotz", "timestamp": 123456789},
            "data": {"temp": 42.42, "hum": 84},
        }
    ]

    transformation = CollectionTransformation(pre=MokshaTransformation().jq(".[] |= pick(.meta, .data.temp)"))

    # Transform data and dump to stdout.
    data_out = transformation.apply(data_in)
    pprint(data_out)


def structure_drop_fields():
    data_in = [
        {
            "meta": {"id": "Hotzenplotz", "timestamp": 123456789},
            "data": {"temp": 42.42, "hum": 84},
        }
    ]

    transformation = CollectionTransformation(pre=MokshaTransformation().jq(".[] |= del(.meta.timestamp, .data.hum)"))

    # Transform data and dump to stdout.
    data_out = transformation.apply(data_in)
    pprint(data_out)


if __name__ == "__main__":
    structure_unwrap_flatten()
    structure_select_fields()
    structure_drop_fields()
