function(doc) {
    if (doc.document_type == 'FormModel' && !doc.void && doc.is_registration_model) {
        emit(doc.form_code, doc);
    }
}