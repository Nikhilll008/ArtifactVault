from rest_framework import serializers

STATUS_CHOICES = [('Active', 'Active'), ('Returned', 'Returned'), ('Overdue', 'Overdue')]


class LoanSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    artifact = serializers.CharField(max_length=150)
    artifactId = serializers.CharField(max_length=20)
    borrower = serializers.CharField(max_length=200)
    loanDate = serializers.DateField()
    dueDate = serializers.DateField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False, default='Active')
    contact = serializers.CharField(max_length=120)

    def validate(self, attrs):
        loan_date = attrs.get('loanDate')
        due_date = attrs.get('dueDate')
        if loan_date and due_date and due_date <= loan_date:
            raise serializers.ValidationError({'dueDate': 'dueDate must be after loanDate.'})
        return attrs

    def to_internal_dates(self, validated_data: dict) -> dict:
        """DateField gives us python date objects; MongoDB documents in
        this project store dates as ISO strings (to match the frontend's
        mock data shape), so convert before saving."""
        data = dict(validated_data)
        for field in ('loanDate', 'dueDate'):
            if field in data and hasattr(data[field], 'isoformat'):
                data[field] = data[field].isoformat()
        return data
