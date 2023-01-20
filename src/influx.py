from datetime import datetime
import influxdb_client                                      # type: ignore
from influxdb_client.client.write_api import SYNCHRONOUS    # type: ignore


class MyDatabase:
    bucket: str
    org: str
    token: str
    url: str

    def __init__(self):
        self.bucket = "test"
        self.org = "nuig"
        self.token = "dJPrO9cYEFJl3Dx3dvp3PxInqiXYAQcIoLoRvOh0hmn0fFjarLPTRDHDDrchzkrkdMkbv7zgta6Qb7WkDQUr-A==" #todo env varibales?
        self.url = "ec2-3-250-216-14.eu-west-1.compute.amazonaws.com:8086"

        self.client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    # function to create line protocol needed to store in db
    def create_line_protocol(self, sensor: str, reading: str, value):
        line: str = "{} {}={} {}"
        timestamp = str(int(datetime.now().timestamp() * 1000))
        return line.format(sensor, reading, value, timestamp)

    def write_db(self, sensor: str, tag: list[str], measurement: str, reading: float) -> int:
        point = influxdb_client.Point(sensor).tag(tag[0], tag[1]).field(measurement, reading)
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        return 1
