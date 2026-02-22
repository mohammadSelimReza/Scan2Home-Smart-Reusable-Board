from rest_framework import serializers
from .models import QRBoard, BoardAssignment
from apps.properties.serializers import PropertyListSerializer
from drf_spectacular.utils import extend_schema_field


class BoardAssignmentSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)

    class Meta:
        model = BoardAssignment
        fields = ('id', 'property', 'assigned_at', 'is_active')


class QRBoardSerializer(serializers.ModelSerializer):
    active_property = serializers.SerializerMethodField()
    assignments = BoardAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = QRBoard
        fields = ('id', 'qr_code_image', 'scan_count', 'active_property', 'assignments', 'created_at')
        read_only_fields = ('id', 'qr_code_image', 'scan_count', 'created_at')

    @extend_schema_field(PropertyListSerializer(allow_null=True))
    def get_active_property(self, obj):
        assignment = obj.assignments.filter(is_active=True).select_related('property').first()
        if assignment:
            return PropertyListSerializer(assignment.property, context=self.context).data
        return None


class ReassignBoardSerializer(serializers.Serializer):
    property_id = serializers.UUIDField()
