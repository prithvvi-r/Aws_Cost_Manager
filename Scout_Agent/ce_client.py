import boto3

class CostExplorerClient:
    def __init__(self):
        # Cost Explorer is global → must be us-east-1
        self.ce = boto3.client("ce", region_name="us-east-1")

    def get_cost_by_service_region(self, start_date, end_date):
        response = self.ce.get_cost_and_usage(
            TimePeriod={
                "Start": start_date,
                "End": end_date
            },
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[
                {"Type": "DIMENSION", "Key": "SERVICE"},
                {"Type": "DIMENSION", "Key": "REGION"}
            ]
        )
        return response
 


