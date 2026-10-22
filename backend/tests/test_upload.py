import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from equipment.models import Dataset, Equipment


def csv_upload(content, name='data.csv'):
    if isinstance(content, str):
        content = content.encode()
    return SimpleUploadedFile(name, content, content_type='text/csv')


class TestUploadAPI:
    def test_upload_success(self, auth_client, user, sample_csv_content):
        r = auth_client.post('/api/upload/', {'file': csv_upload(sample_csv_content), 'name': 'My data'}, format='multipart')
        assert r.status_code == 201, r.data
        assert r.data['name'] == 'My data'
        assert r.data['total_count'] == 5
        assert r.data['type_distribution'] == {'Pump': 2, 'Valve': 1, 'Reactor': 1, 'Column': 1}
        dataset = Dataset.objects.get(pk=r.data['id'])
        assert dataset.uploaded_by == user
        assert Equipment.objects.filter(dataset=dataset).count() == 5

    def test_upload_requires_auth(self, api_client, sample_csv_content, db):
        r = api_client.post('/api/upload/', {'file': csv_upload(sample_csv_content)}, format='multipart')
        assert r.status_code == 401
        assert Dataset.objects.count() == 0

    def test_upload_missing_file(self, auth_client):
        assert auth_client.post('/api/upload/', {}, format='multipart').status_code == 400

    @pytest.mark.parametrize('filename', ['data.txt', 'data.csv.exe', 'data.xlsx', 'shell.php'])
    def test_upload_rejects_non_csv_extension(self, auth_client, sample_csv_content, filename):
        r = auth_client.post('/api/upload/', {'file': csv_upload(sample_csv_content, filename)}, format='multipart')
        assert r.status_code == 400

    def test_upload_rejects_binary_disguised_as_csv(self, auth_client):
        payload = b'PK' + bytes([3, 4, 0, 0]) + bytes(100)
        r = auth_client.post('/api/upload/', {'file': csv_upload(payload, 'evil.csv')}, format='multipart')
        assert r.status_code == 400
        assert Dataset.objects.count() == 0

    def test_upload_rejects_oversized_file(self, auth_client, settings):
        settings.MAX_UPLOAD_BYTES = 1024
        big = 'Equipment Name,Type,Flowrate,Pressure,Temperature\n' + 'Pump,Pump,1,1,1\n' * 200
        r = auth_client.post('/api/upload/', {'file': csv_upload(big)}, format='multipart')
        assert r.status_code == 413
        assert Dataset.objects.count() == 0

    def test_upload_missing_columns(self, auth_client):
        r = auth_client.post('/api/upload/', {'file': csv_upload('Name,Type\nPump,Pump\n')}, format='multipart')
        assert r.status_code == 400
        assert 'Missing required columns' in r.data['detail']

    def test_upload_empty_file(self, auth_client):
        assert auth_client.post('/api/upload/', {'file': csv_upload('')}, format='multipart').status_code == 400

    def test_upload_non_numeric_values_do_not_crash(self, auth_client):
        content = 'Equipment Name,Type,Flowrate,Pressure,Temperature\nPump-1,Pump,abc,2,3\nPump-2,Pump,5,6,7\n'
        r = auth_client.post('/api/upload/', {'file': csv_upload(content)}, format='multipart')
        assert r.status_code == 201, r.data

    def test_upload_long_name_is_truncated(self, auth_client, sample_csv_content):
        r = auth_client.post('/api/upload/', {'file': csv_upload(sample_csv_content), 'name': 'n' * 1000}, format='multipart')
        assert r.status_code == 201
        assert len(r.data['name']) == 255

    def test_path_traversal_filename_stays_inside_media_root(self, auth_client, sample_csv_content, settings):
        r = auth_client.post('/api/upload/', {'file': csv_upload(sample_csv_content, '../../evil.csv')}, format='multipart')
        assert r.status_code == 201, r.data
        stored = Dataset.objects.get(pk=r.data['id']).csv_file.path
        root = str(settings.MEDIA_ROOT)
        assert stored.startswith(root)
        assert '..' not in stored[len(root):]

    def test_uploads_are_not_served_without_debug(self, api_client, auth_client, sample_csv_content):
        r = auth_client.post('/api/upload/', {'file': csv_upload(sample_csv_content)}, format='multipart')
        url = Dataset.objects.get(pk=r.data['id']).csv_file.url
        assert api_client.get(url).status_code == 404

    def test_upload_is_rate_limited(self, auth_client, sample_csv_content):
        codes = [
            auth_client.post('/api/upload/', {'file': csv_upload(sample_csv_content)}, format='multipart').status_code
            for _ in range(22)
        ]
        assert 429 in codes
