class RecordNotFoundException(Exception):
    def __init__(self, model_name, record_id, *args, **kwargs):
        super(RecordNotFoundException, self).__init__(*args, **kwargs)
        self.model_name = model_name
        self.record_id = record_id

    def __repr__(self):
        return f"Record: {self.record_id} for Model {self.model_name} not found"
