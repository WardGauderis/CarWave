from flask_wtf import FlaskForm


class DictForm(FlaskForm):
    all_errors = dict()

    def generator(self):
        for attr, value in self.__dict__.items():
            if hasattr(value, 'data'):
                yield attr, value.data

    def load_json(self, json):
        for key, value in json.items():
            if hasattr(self, key):
                attr = getattr(self, key)
                if not isinstance(value, str):
                    self.all_errors[key] = "This field should be string."
                else:
                    attr.process_formdata([value])

    def validate_json(self):
        self.validate()
        self.errors.pop('csrf_token')
        return not (len(self.errors) + len(self.all_errors))

    def get_errors(self):
        tmp = dict(list(self.errors.items()) + list(self.all_errors.items()))
        self.all_errors.clear()
        return tmp
