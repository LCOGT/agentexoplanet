from rest_framework import serializers

from agentex.datareduc import fitsanalyse

class MeasurementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    x = serializers.JSONField()
    y = serializers.JSONField()
    entrymode = serializers.CharField(max_length=1)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        data = fitsanalyse(validated_data)
        return data
