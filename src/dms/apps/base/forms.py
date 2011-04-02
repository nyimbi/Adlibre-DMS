"""
Module: Base Django Forms
Project: Adlibre DMS
Copyright: Adlibre Pty Ltd 2011
License: See LICENSE for license information
"""

import pickle

from django import forms

from base.models import (available_validators, available_securities,
    available_doccodes, available_storages, Rule)
from base.utils import DocCodeProvider


def doccode_choices():
    doccodes = []
    for doccode, plugin in available_doccodes().items():
        doccodes.append([doccode, '%s - %s' % (doccode, plugin.description)])
    return doccodes


def validator_choices():
    validators = []
    for validator, plugin in available_validators().items():
        validators.append([validator, '%s - %s' % (validator, plugin.description)])
    return validators


def storage_choices():
    storages = []
    for storage in available_storages():
        storages.append([storage, storage])
    return storages


def security_choices():
    securities = []
    for security in available_securities():
        securities.append([security, security])
    return securities



class SettingForm(forms.Form):
    doccode = forms.ChoiceField(label="DocCode Validator", choices=doccode_choices())
    storage = forms.ChoiceField(label="Storage", choices=storage_choices())
    validators = forms.MultipleChoiceField(label="Validators",
        choices=validator_choices(), required=False)
    securities = forms.MultipleChoiceField(label="Securities",
        choices=security_choices(), required=False)

    def clean_doccode(self):
        """
        Make sure doccode is unique
        """
        doccode = self.cleaned_data['doccode']
        if Rule.objects.filter(doccode=pickle.dumps(DocCodeProvider.plugins[doccode]())).exists():
            raise forms.ValidationError("DocCode must be unique")
        return doccode


class EditSettingForm(forms.Form):
    """
    Edit rule, only allow to change storage, validators and securities
    """
    storage = forms.ChoiceField(label="Storage", choices=storage_choices())
    validators = forms.MultipleChoiceField(label="Validators",
        choices=validator_choices(), required=False)
    securities = forms.MultipleChoiceField(label="Securities",
        choices=security_choices(), required=False)

