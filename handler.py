import gittoolkit as git
import xqueue_adapter as xqueue

import os
import shutil
import json
import datetime
import commands
import codecs

WORKING_STAGE = 'development'
WORK_ROOT = '/Users/Joe/Study/Project/autograder/'

def Handle(job, queue_name, cookie):
    print str(datetime.datetime.now())
    job = json.loads(job)
    hw_info = json.loads(job['xqueue_body'])
    # hw_info = job['xqueue_body']
    dir_name = _create_working_dir(str(json.loads(job['xqueue_header'])['submission_id']))
    student_info  = json.loads(hw_info['student_info'])
    student_name = student_info['anonymous_student_id']
    payload = json.loads(hw_info['grader_payload'])
    exp_id = payload['exp_id']
    file_path = payload['file_path']
    print '\t student_name: {}'.format(student_name)
    print '\t experiment ID: {}'.format(exp_id)
    print '\t file_path: {}'.format(file_path)
    status = _get_remote_file(student_name, exp_id, file_path)
    grader_response = _grade('AutoGraderUser', dir_name)
    response = _generate_response(job)
    _response(cookie, job, response)
    _remove_working_dir(dir_name)

def _create_working_dir(dir_name):
    os.chdir('./{}'.format(WORKING_STAGE))
    if dir_name in os.listdir('.'):
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)
    os.chdir(dir_name)
    return dir_name

def _get_remote_file(user_name, exp_id, file_path):
    status, file_content = git.GetRepoFile(user_name, exp_id, file_path)
    with codecs.open('answer', 'w', encoding='utf8') as f_out:
        f_out.write(unicode(file_content, 'UTF-8'))
    return status

def _generate_response(job):
    with codecs.open('response', 'r', encoding='utf8') as f_in:
        grad = f_in.readline().strip('\n')
        grad = int(grad)
        full_mark = f_in.readline().strip('\n')
        full_mark = int(full_mark)
        comments = f_in.read()
    body = {
        'correct':grad==full_mark,
        'score':grad,
        'msg':comments
    }
    print body
    return body

def _response(cookie, job, body):
    xqueue.ReturnResult(cookie, job['xqueue_header'], body)

def _remove_working_dir(dir_name):
    os.chdir('..')
    shutil.rmtree(dir_name)
    os.chdir('..')

def _grade(grader_name, dir_name):
    os.chdir('{}grader'.format(WORK_ROOT))
    output = commands.getoutput('java {} ../development/{}/'.format(grader_name, dir_name))
    os.chdir('../development/{}'.format(dir_name))
    print '\t Script output:'
    print output
