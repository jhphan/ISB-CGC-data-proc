'''
Created on Apr 30, 2015

currently does nothing TODO: the current policy is to delete contents of GCS buckets, this can be 
updated to carry that out rather than have it be done manually

Copyright 2015, Institute for Systems Biology.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: michael
'''
# from gcloud import datastore

def prepare_upload(tumor_type2platform2archive_types2archives, log):
    """
    prepares the current state of the project for the latest upload.  uses the 
    passed in archives to determine out of date files and deletes the current
    ISBCGCmetadata from the backing store
    """
    return