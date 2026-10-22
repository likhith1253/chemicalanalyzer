from django.core.files.uploadedfile import SimpleUploadedFile

from equipment.models import Dataset


class TestDatasetsAPI:
    def test_list_empty(self, auth_client):
        r = auth_client.get('/api/datasets/')
        assert r.status_code == 200
        assert r.data == []

    def test_list_returns_own_datasets_newest_first(self, auth_client, multiple_datasets):
        r = auth_client.get('/api/datasets/')
        assert r.status_code == 200
        assert [d['name'] for d in r.data] == ['Test Dataset 3', 'Test Dataset 2', 'Test Dataset 1']

    def test_list_requires_auth(self, api_client, db):
        assert api_client.get('/api/datasets/').status_code == 401

    def test_detail(self, auth_client, equipment_dataset):
        r = auth_client.get(f'/api/datasets/{equipment_dataset.id}/')
        assert r.status_code == 200
        assert r.data['name'] == 'Test Dataset'
        assert r.data['total_count'] == 5
        assert r.data['type_distribution']['Pump'] == 2
        assert 'preview_rows' in r.data
        assert 'csv_file' not in r.data

    def test_detail_not_found(self, auth_client):
        assert auth_client.get('/api/datasets/99999/').status_code == 404

    def test_detail_requires_auth(self, api_client, equipment_dataset):
        assert api_client.get(f'/api/datasets/{equipment_dataset.id}/').status_code == 401

    def test_only_last_five_datasets_are_kept(self, auth_client, user, sample_csv_content):
        for i in range(7):
            Dataset.objects.create(
                name=f'D{i}', original_filename='x.csv', uploaded_by=user,
                csv_file=SimpleUploadedFile('x.csv', sample_csv_content.encode()),
            )
        assert Dataset.objects.filter(uploaded_by=user).count() == 5
        assert len(auth_client.get('/api/datasets/').data) == 5
