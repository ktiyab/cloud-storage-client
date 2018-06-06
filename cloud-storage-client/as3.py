import boto3
import tarfile
import os

class AS3Client():
    """ 
    Boto3 Client to connect with Amazon S3 storage
    """

    def __init__(self, bucket_name, access_key, secret_key):
        session = boto3.Session(access_key, secret_key)
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.client = session.client('s3')
        self.resource = session.resource('s3')

    def delete_file(self, file_path):
        bucket = self.resource.Bucket(self.bucket_name)
        for obj in bucket.objects.filter(Prefix=file_path):
            obj.delete()

    def delete_folder(self, folder_id):
        bucket = self.resource.Bucket(self.bucket_name)
        for obj in bucket.objects.filter(Prefix=folder_id + '/'):
            obj.delete()
            
    def download_folder(self, folder_id, folder_output):
        bucket = self.resource.Bucket(self.bucket_name)
        if not os.path.exists(folder_output):
            os.makedirs(folder_output)
        for obj in bucket.objects.filter(Prefix=folder_id + '/'):
            splitted_name = obj.key.split('/')
            bucket.download_file(obj.key, folder_output + '/' + splitted_name[len(splitted_name) - 1])
    
    def upload_file(self, src_file, dst_file):
        self.client.upload_file(src_file, self.bucket_name, dst_file)

    def upload_files(self, folder_id, selected_chunks, folder_chunks, do_tar=False, do_compress=False):
        if do_tar:
            if do_compress:
                ext = '.tgz'
            else:
                ext = '.tar'

            folder_compress = '/tmp/' + folder_id + ext
            with tarfile.open(folder_compress, 'a') as tar:
                for chunk in selected_chunks:
                    tar.add(chunk)
                tar.close()    
            self.client.upload_file(folder_compress, self.bucket_name, folder_id + '/' + folder_id + ext)
        else:
            for chunk in selected_chunks:
                self.client.upload_file(folder_chunks + '/' + chunk, self.bucket_name, folder_id + '/' + chunk)

    def download_file(self, folder_id, selected_chunk, folder_output):
        bucket = self.resource.Bucket(self.bucket_name)
        if not os.path.exists(folder_output):
            os.makedirs(folder_output)
        bucket.download_file(folder_id + '/' + selected_chunk, folder_output + '/' + selected_chunk)

    def upload_folder(self, folder_id, folder_results, do_tar=False, do_compress=False):
        if do_tar:
            if do_compress:
                ext = '.tgz'
                verb = 'w:gz'
            else:
                ext = '.tar'
                verb = 'w'

            folder_compress = '/tmp/' + folder_id + ext
            with tarfile.open(folder_compress, verb) as tar:
                tar.add(folder_results, arcname=folder_id)
            tar.close()
            self.client.upload_file(folder_compress, self.bucket_name, folder_id + '/' + folder_id + ext)
        else:
            dir = os.fsencode(folder_results)
            for file in os.listdir(dir):
                filePath = folder_results + '/' + file.decode('utf-8')
                if not os.path.isdir(filePath):
                    self.client.upload_file(filePath, self.bucket_name, folder_id + '/' + file.decode('utf-8'))