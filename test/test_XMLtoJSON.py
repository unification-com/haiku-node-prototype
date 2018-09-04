import json

import pytest
import xmljson

from lxml.etree import fromstring

schema_1 = "<schema-template><fields><field><name>account_name</name><type>varchar</type><is-null>false</is-null><table>unification_lookup</table></field><field><name>Heartrate</name><type>int</type><is-null>true</is-null><table>data_1</table></field><field><name>GeoLocation</name><type>int</type><is-null>true</is-null><table>data_1</table></field><field><name>TimeStamp</name><type>int</type><is-null>true</is-null><table>data_1</table></field><field><name>Pulse</name><type>int</type><is-null>true</is-null><table>data_1</table></field></fields></schema-template>"  # noqa
schema_2 = "<schema-template><fields><field><name>account_name</name><type>varchar</type><is-null>false</is-null><table>unification_lookup</table></field><field><name>DataBlob</name><type>binarydata</type><is-null>true</is-null><table>data_1</table></field><field><name>BlobSize</name><type>int</type><is-null>true</is-null><table>data_1</table></field></fields></schema-template>"  # noqa
schema_3 = "<schema-template><fields><field><name>account_name</name><type>varchar</type><is-null>false</is-null><table>unification_lookup</table></field><field><name>Image</name><type>base64_mime_image</type><is-null>true</is-null><table>data_1</table></field></fields></schema-template>"  # noqa


@pytest.mark.parametrize("xml_str", [schema_1, schema_2, schema_3])
def test_xml_to_json(xml_str):
    xml = fromstring(xml_str)
    json_str = json.dumps(xmljson.gdata.data(xml))
    d = json.loads(json_str)
    print(json_str)
    print(d)
