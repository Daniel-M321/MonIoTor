import os
import influxdb_client                                      # type: ignore
from influxdb_client.client.write_api import SYNCHRONOUS    # type: ignore


class MyDatabase:
    bucket: str
    org: str
    token: str
    url: str

    def __init__(self):
        self.bucket = "sensors"
        self.org = "nuig"
        self.token = os.environ["INFLUX_TOKEN"]
        self.url = os.environ["INFLUX_URL"]

        self.client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def write_db(self, sensor: str, tag: list[str], measurement: str, reading: float) -> int:
        try:
            point = influxdb_client.Point(sensor).tag(tag[0], tag[1]).field(measurement, reading)
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        except Exception as e:
            print(e)
            return 0
        return 1

    def query_db(self, measurement, location, field, period="2y") -> list[str]:
        results = []
        try:
            query = 'from(bucket:"{0}")\
            |> range(start: -{1})\
            |> filter(fn:(r) => r._measurement == "{2}")\
            |> filter(fn:(r) => r.location == "{3}")\
            |> filter(fn:(r) => r._field == "{4}")'.format(self.bucket, period, measurement, location, field)

            result = self.query_api.query(org=self.org, query=query)

            for table in result:
                for record in table.records:
                    results.append(record.get_value())
        except Exception as e:
            print(e)

        return results


