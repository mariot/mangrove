from mangrove.datastore.database import DataObject
from mangrove.datastore.documents import ReportConfigDocument, ReportConfigDocumentBase, ExternalReportConfigDocument, \
    EntityReportConfigDocument


def get_report_configs(manager):
    rows = manager.load_all_rows_in_view('all_report_configs')
    if len(rows):
        sorted_rows = sorted(rows, key=lambda row: 'order' in row['value'] and row['value']['order'] or 0)
        return [ReportConfigBase.config(manager, ReportConfigDocumentBase.document(row['value'])) for row in sorted_rows]
    return None


def get_report_config(manager, id):
    rows = manager.load_all_rows_in_view('all_report_configs', key=id)
    if len(rows):
        return ReportConfigBase.config(manager, ReportConfigDocumentBase.document(rows[0]['value']))
    return None


class ReportConfigBase(DataObject):
    @classmethod
    def config(cls, dbm, document):
        if isinstance(document, ExternalReportConfigDocument):
            return ExternalReportConfig.new_from_doc(dbm, document)
        elif isinstance(document, EntityReportConfigDocument):
            return EntityReportConfig.new_from_doc(dbm, document)
        else:
            return ReportConfig.new_from_doc(dbm, document)

    @property
    def id(self):
        return self._doc.id

    @property
    def name(self):
        return self._doc.name

    @property
    def template_url(self):
        return self._doc.template_url

    @property
    def total_in_label(self):
        return self._doc.total_in_label
    
    def template(self):
        return self._get_attachment("index.html")

    def file(self, file_name):
        return self._get_attachment(file_name)

    def _get_attachment(self, file_name):
        try:
            return self.get_attachment(self._doc.id, filename=file_name)
        except LookupError:
            return ''


class ReportConfig(ReportConfigBase):
    __document_class__ = ReportConfigDocument

    def __init__(self, dbm, name=None, questionnaires=None, **kwargs):
        super(ReportConfig, self).__init__(dbm)
        DataObject._set_document(self, ReportConfigDocument())
        self._create_new_report_config_doc(name, questionnaires)

    def _create_new_report_config_doc(self, name, questionnaires):
        self._doc.name = name
        self._doc.questionnaires = questionnaires

    @property
    def questionnaires(self):
        return self._doc.questionnaires

    @property
    def date_filter(self):
        return self._doc.date_filter

    @property
    def filters(self):
        return self._doc.filters

    @property
    def sort_fields(self):
        return self._doc.sort_fields


class ExternalReportConfig(ReportConfigBase):
    __document_class__ = ExternalReportConfigDocument

    def __init__(self, dbm, **kwargs):
        super(ExternalReportConfig, self).__init__(dbm)
        DataObject._set_document(self, ExternalReportConfigDocument())

    @property
    def url(self):
        return self._doc.url

    @property
    def description(self):
        return self._doc.description


class EntityReportConfig(ReportConfigBase):
    __document_class__ = EntityReportConfigDocument

    def __init__(self, dbm, **kwargs):
        super(EntityReportConfig, self).__init__(dbm)
        DataObject._set_document(self, EntityReportConfigDocument())

    @property
    def filters(self):
        return self._doc.filters

    @property
    def details(self):
        return self._doc.details

    @property
    def specials(self):
        return self._doc.specials

    @property
    def fallback_location(self):
        return self._doc.fallback_location

    @property
    def entity_type(self):
        return self._doc.entity_type
