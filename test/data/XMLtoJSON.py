import json, xmljson
from lxml.etree import fromstring, tostring

schema_1 = "<schema-template><fields><field><name>account_name</name><type>varchar</type><is-null>false</is-null><table>unification_lookup</table></field><field><name>Heartrate</name><type>int</type><is-null>true</is-null><table>data_1</table></field><field><name>GeoLocation</name><type>int</type><is-null>true</is-null><table>data_1</table></field><field><name>TimeStamp</name><type>int</type><is-null>true</is-null><table>data_1</table></field><field><name>Pulse</name><type>int</type><is-null>true</is-null><table>data_1</table></field></fields></schema-template>"
schema_2 = "<schema-template><fields><field><name>account_name</name><type>varchar</type><is-null>false</is-null><table>unification_lookup</table></field><field><name>DataBlob</name><type>binarydata</type><is-null>true</is-null><table>data_1</table></field><field><name>BlobSize</name><type>int</type><is-null>true</is-null><table>data_1</table></field></fields></schema-template>"
schema_3 = "<schema-template><fields><field><name>account_name</name><type>varchar</type><is-null>false</is-null><table>unification_lookup</table></field><field><name>Image</name><type>base64_mime_image</type><is-null>true</is-null><table>data_1</table></field></fields></schema-template>"


def xml_to_json(xml_str):
    xml = fromstring(xml_str)
    json_str = json.dumps(xmljson.gdata.data(xml))     #this is a string
    data = json.loads(json_str)                        #this is a dictionary
    print(json_str)
    print(data)


xml_to_json(schema_1)
