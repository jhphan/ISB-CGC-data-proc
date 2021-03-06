'''
Created on Nov 25, 2015

part of solution for mdmiller53/software-engineering-coordination/#798

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
from datetime import date
from datetime import datetime
import json
import logging
import sys

import isbcgc_cloudsql_model
from util import create_log

def update_nulls(config, log):
    update_null_stmts = [
        'update metadata_samples set has_Illumina_DNASeq = 0 where has_Illumina_DNASeq is null',
        'update metadata_samples set has_BCGSC_HiSeq_RNASeq = 0 where has_BCGSC_HiSeq_RNASeq is null',
        'update metadata_samples set has_UNC_HiSeq_RNASeq = 0 where has_UNC_HiSeq_RNASeq is null',
        'update metadata_samples set has_BCGSC_GA_RNASeq = 0 where has_BCGSC_GA_RNASeq is null',
        'update metadata_samples set has_UNC_GA_RNASeq = 0 where has_UNC_GA_RNASeq is null',
        'update metadata_samples set has_HiSeq_miRnaSeq = 0 where has_HiSeq_miRnaSeq is null',
        'update metadata_samples set has_GA_miRNASeq = 0 where has_GA_miRNASeq is null',
        'update metadata_samples set has_RPPA = 0 where has_RPPA is null',
        'update metadata_samples set has_SNP6 = 0 where has_SNP6 is null',
        'update metadata_samples set has_27k = 0 where has_27k is null',
        'update metadata_samples set has_450k = 0 where has_450k is null'
    ]
    for update_null_stmt in update_null_stmts:
        isbcgc_cloudsql_model.ISBCGC_database_helper.update(config, update_null_stmt, log, [])

def updateDatafileUploaded(config, path_file, log):
    try:
        select_stmt = 'select datafilename from metadata_data where datafilename = %s group by datafilename'
        found_path_names = []
        notfound_path_names = []
        count = 0
        log.info('\tprocessing path/name combinations from %s for existence in the database' % (path_file))
        for path in path_file:
            path = path.strip()
            filename = path[path.rindex('/') + 1:]
            if 0 == count % 8192:
                log.info('\tprocessing %s record: %s:%s' % (count, path, filename))
            count += 1
            # check that the file was actually part of the metadata
            cursor = isbcgc_cloudsql_model.ISBCGC_database_helper.select(config, select_stmt, log, [filename], False)
            if 0 < len(cursor):
                found_path_names += [[path, filename]]
            elif not filename.endswith('xml'):
                notfound_path_names += [[path, filename]]
        if 0 == len(notfound_path_names):
            log.info('\tprocessed a total of %s path/name combinations.' % (count))
        else:
            if 500 > len(notfound_path_names):
                print_notfound = notfound_path_names
            else:
                print_notfound = notfound_path_names[:500] + ['...']
            log.info('\tprocessed a total of %s path/name combinations.  %s files were not found:\n\t\t%s\n' % (count, len(notfound_path_names), '\n\t\t'.join(':'.join(pathinfo) for pathinfo in print_notfound)))

        update_stmt = 'update metadata_data set DatafileUploaded = \'true\', DatafileNameKey = %s where DatafileName = %s'
        isbcgc_cloudsql_model.ISBCGC_database_helper.update(config, update_stmt, log, found_path_names, False)
    except Exception as e:
        log.exception('\tproblem updating')
        raise e

def main(configfilename):
    print datetime.now(), 'begin update DatafileUploaded'
    with open(configfilename) as configFile:
        config = json.load(configFile)
    
    log_dir = str(date.today()).replace('-', '_') + '_' + config['log_dir_tag'] + '_update_uploaded' + '/'
    log_name = create_log(log_dir, 'top_processing')
    log = logging.getLogger(log_name)
    log.info('begin update DatafileUploaded')
    try:
        for path_file in config['buckets']['update_uploaded']:
            with open(path_file, 'r') as paths:
                updateDatafileUploaded(config, paths, log)
    
        update_nulls(config, log)
    except Exception as e:
        log.exception('problem updating DatafileUploaded')
        raise e
    log.info('finish update DatafileUploaded')
    print datetime.now(), 'finish update DatafileUploaded'

if __name__ == '__main__':
    main(sys.argv[1])
