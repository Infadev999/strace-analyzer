from flask import Flask, render_template, request,redirect
from werkzeug.utils import secure_filename
import os
import re
import time

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '\strace_data_files/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# limit upload size upto 50MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.route('/')
def upload_file():
    return render_template("file_upload_form.html")

@app.route('/uploader',methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        f=request.files['file']
        if f.filename == '':
            print('No file selected')
            return redirect(request.url)
        if f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            options = []
            if request.form.get("Op1"):
                options.append(1)
            if request.form.get("Op2"):
                options.append(2)
            if request.form.get("Op3"):
                options.append(3)
            if request.form.get("Op4"):
                options.append(4)
            results,keys = strace(options,filename)
    return render_template("results.html",results=results, keys = keys)


def strace(options, filename):
    print("Initializing strace variables")
    count_read = 0
    count_write = 0

    count_all = 0
    count_read_between_10_and_99 = 0
    count_read_more_than_100 = 0
    count_write_between_10_and_99 = 0
    count_write_more_than_100 = 0
    count_read_morethan_1sec = 0
    count_write_morethan_1sec = 0

    # dictionary to store output values
    dict_outputs = dict()
    dict_outputs = {'Total read and write operations': 1, 'read/write between 10 and 99': 2,
                    'read/write between 100ms and 1 sec': 3, 'read/write greater than 1 sec': 4}

    # REGEX patterns
    print("Initializing regex variables")
    pattern_morethan_one_second = r'<[1-9]+[0-9]*\.'
    pattern_read_between_10_and_99 = r'.*(read\()+.*<0\.0?[1-9]+'
    pattern_read_more_than_100 = r'.*(read\()+.*<0\.[1-9]+'
    pattern_write_between_10_and_99 = r'.*(write\()+.*<0\.0?[1-9]+'
    pattern_write_more_than_100 = r'.*(write\()+.*<0\.[1-9]+'

    # read/write more than 1 second
    pattern_read_greater_than_1sec = r'.*(read\()+.*<[1-9]+[0-9]*\.'
    pattern_write_greater_than_1sec = r'.*(write\()+.*<[1-9]+'

    #    options = input().split(',')
    #    print(options)

    #    checked = []
    #
    #    for i in options:
    #        #if i in dict_outputs.keys():
    #        checked.append(dict_outputs[i])
    #    print(checked)
    checked = options
    print("Opening file {}".format(filename))
    start_time = time.time()
    with open(UPLOAD_FOLDER + filename, 'r') as f1:
        for line in f1:
            print(line)
            # Total number of READ calls
            if 'read' in line:
                if '=' in line:
                    count_read += 1
                    # Total number of WRITE cals
            if 'write' in line:
                if '=' in line:
                    count_write += 1
            match_ALL_morethan_1_second = re.search(pattern_morethan_one_second, line)
            match_READ_between_10_and_99 = re.search(pattern_read_between_10_and_99, line)
            match_READ_more_than_100 = re.search(pattern_read_more_than_100, line)
            match_WRITE_between_10_and_99 = re.search(pattern_write_between_10_and_99, line)
            match_WRITE_more_than_100 = re.search(pattern_write_more_than_100, line)
            match_READ_morethan_1_second = re.search(pattern_read_greater_than_1sec, line)
            match_WRITE_morethan_1_second = re.search(pattern_write_greater_than_1sec, line)

            if match_ALL_morethan_1_second != None:
                # print(match.group().split('<')[1].split('.')[0])
                count_all += 1
            if match_READ_between_10_and_99 != None:
                count_read_between_10_and_99 += 1
            if match_READ_more_than_100 != None:
                count_read_more_than_100 += 1
            if match_WRITE_between_10_and_99 != None:
                count_write_between_10_and_99 += 1
            if match_WRITE_more_than_100 != None:
                count_write_more_than_100 += 1

            if match_READ_morethan_1_second != None:
                count_read_morethan_1sec += 1
            if match_WRITE_morethan_1_second != None:
                count_write_morethan_1sec += 1
    print("completed performing REGEX operations.")
    print("--- %s seconds ---" % (time.time() - start_time))

    results = dict()
    results = {'Total Number of READ system calls': 0, 'Total Number of WRITE system calls': 0,
               'Read Between 10 and 99 milliseconds': 0, 'Write Between 10 and 99 milliseconds': 0,
               'Read Between 100 and 999 milliseconds': 0, 'Write Between 100 and 999 milliseconds': 0,
               'Total number of system calls which took more than 1 second': 0,
               'Total number of read system calls which took more than 1 second': 0,
               'Total number of write system calls which took more than 1 second': 0}
    for i in checked:
        if i == 1:
            results['Total Number of READ system calls'] = count_read
            results['Total Number of WRITE system calls'] = count_write
        else:
            results['Total Number of READ system calls'] = 0
            results['Total Number of WRITE system calls'] = 0

        if i == 2:
            results['Read Between 10 and 99 milliseconds'] = count_read_between_10_and_99
            results['Write Between 10 and 99 milliseconds'] = count_write_between_10_and_99
        else:
            results['Read Between 10 and 99 milliseconds'] = 0
            results['Write Between 10 and 99 milliseconds'] = 0

        if i == 3:
            results['Read Between 100 and 999 milliseconds'] = count_read_more_than_100
            results['Write Between 100 and 999 milliseconds'] = count_write_more_than_100
        else:
            results['Read Between 100 and 999 milliseconds'] = 0
            results['Write Between 100 and 999 milliseconds'] = 0

        if i == 4:
            results['Total number of system calls which took more than 1 second'] = count_all
            results['Total number of read system calls which took more than 1 second'] = count_read_morethan_1sec
            results['Total number of read system calls which took more than 1 second'] = count_write_morethan_1sec
        else:
            results['Total number of read system calls which took more than 1 second'] = 0
            results['Total number of read system calls which took more than 1 second'] = 0

    return results, results.keys()
if __name__ == '__main__':
    app.run(debug=True)