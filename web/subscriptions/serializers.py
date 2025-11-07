from rest_framework import serializers
import phonenumbers

class SubscribeSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate_phone(self, value):
        try:
            parsed = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed):
                raise serializers.ValidationError('Invalid phone number')
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError('Invalid phone number format')
        return value
