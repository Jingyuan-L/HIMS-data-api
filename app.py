from flask import Flask, request, make_response
import cx_Oracle

app = Flask(__name__)


sql_expense = "SELECT * FROM expense WHERE date between to_date(:1,'yyyy-mm-dd') and to_date(:2,'yyyy-mm-dd') " \
              "and hospital_id = :3"
sql_flow_hospital = "SELECT * FROM flow WHERE date between to_date(:1,'yyyy-mm-dd') and to_date(:2,'yyyy-mm-dd') " \
                    "and hospital_id = :3"
sql_flow_doctor = "SELECT * FROM flow WHERE date between to_date(:1,'yyyy-mm-dd') and to_date(:2,'yyyy-mm-dd') " \
                  "and hospital_id = :3 and doctor_id = :4"
sql_occupancy = "SELECT * FROM occupancy WHERE occu_date between to_date(:1,'yyyy-mm-dd') and to_date(:2,'yyyy-mm-dd') " \
                "and hospital_id = :3"


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/duration')
def show_duration():
    db = cx_Oracle.connect('admin/12345678@oracle-hims-warehouse.cpfsluvxtsqc.us-east-2.rds.amazonaws.com:1521/ORCL')
    cur = db.cursor()

    items = []
    if request.args['info'] == "":
        cur.execute("SELECT * FROM duration")
    else:
        print("'%" + request.args['info'] + "%'")
        cur.execute("SELECT * FROM duration WHERE description LIKE :1", ("%%" + request.args['info'] + "%%",))

    for icd, des, total, dur in cur.fetchall():
        items.append({
            'icd_code': icd,
            'description': des,
            'total_times': total,
            'duration': dur,
        })

    return make_response({
        'items': items,
    })


@app.route('/expense')
def show_expense():

    return make_response()


@app.route('/flow')
def show_flow():

    return make_response()


@app.route('/occupancy')
def show_occupancy():

    return make_response()


if __name__ == '__main__':
    app.run(debug=True, port=8881)
