class TestPDFReportAPI:
    def test_pdf_download(self, auth_client, equipment_dataset):
        r = auth_client.get(f'/api/datasets/{equipment_dataset.id}/report/pdf/')
        assert r.status_code == 200
        assert r['Content-Type'] == 'application/pdf'
        assert 'attachment' in r['Content-Disposition']
        assert r.content.startswith(b'%PDF-')

    def test_pdf_requires_auth(self, api_client, equipment_dataset):
        assert api_client.get(f'/api/datasets/{equipment_dataset.id}/report/pdf/').status_code == 401

    def test_pdf_not_found(self, auth_client):
        assert auth_client.get('/api/datasets/99999/report/pdf/').status_code == 404

    def test_pdf_special_characters_in_name(self, auth_client, equipment_dataset):
        equipment_dataset.name = 'A <b>&</b> "quoted" dataset'
        equipment_dataset.save()
        r = auth_client.get(f'/api/datasets/{equipment_dataset.id}/report/pdf/')
        assert r.status_code == 200
