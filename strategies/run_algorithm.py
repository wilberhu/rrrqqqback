import os
import re
import codecs


def save_file(request, folder, user, id):
    title = re.sub('[^a-zA-Z0-9_]', '', request.data["title"].strip().replace(" ", ""))

    py_folder = os.path.join(folder, user, "id"+id)
    if not os.path.exists(py_folder):
        os.makedirs(py_folder)

    f = codecs.open(os.path.join(py_folder, title + ".py"), "w", 'utf-8')
    f.write(request.data['code'].encode('utf-8').decode('utf-8'))
    f.close()