from flask import Flask, request, make_response
import cx_Oracle
import datetime

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/dashboard')
def set_dashboard():
    db = cx_Oracle.connect('admin/12345678@oracle-hims-warehouse.cpfsluvxtsqc.us-east-2.rds.amazonaws.com:1521/ORCL')
    cur = db.cursor()

    yesterday = datetime.date.today() - datetime.timedelta(days=30)
    today = datetime.date.today()
    yesterday = str(yesterday)
    today = str(today)
    print(yesterday, today)

    cur.execute("SELECT sum(expense) FROM expense "
                "WHERE expe_date between to_date(:1,'yyyy-mm-dd') and to_date(:2,'yyyy-mm-dd')",
                (yesterday, today))
    expense_num = cur.fetchone()[0]

    cur.execute("SELECT SUM(times) FROM flow "
                "WHERE flow_date between to_date(:1,'yyyy-mm-dd') and to_date(:2,'yyyy-mm-dd')",
                (yesterday, today))
    patients_num = cur.fetchone()[0]

    cur.execute("SELECT AVG(occupied_rm_num / total_rm * 100) FROM occupancy "
                "WHERE occu_date between to_date(:1,'yyyy-mm-dd') and to_date(:2,'yyyy-mm-dd')",
                (yesterday, today))
    occupancy_rate = cur.fetchone()[0]
    print(expense_num, patients_num, occupancy_rate)

    return make_response({
        'expense_num': expense_num,
        'patients_num': patients_num,
        'occupancy_rate': format("%.2f" % occupancy_rate),
    })


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
    sql_expense = "SELECT expe_date, expense FROM expense " \
                  "WHERE expe_date between to_date(:1,'yyyy') and to_date(:2,'yyyy') " \
                  "and hospital_id = :3"
    db = cx_Oracle.connect('admin/12345678@oracle-hims-warehouse.cpfsluvxtsqc.us-east-2.rds.amazonaws.com:1521/ORCL')
    cur = db.cursor()
    start = request.args['query_year']
    end = str(int(request.args['query_year']) + 1)
    id = request.args['hospital_id']
    cur.execute(sql_expense, (start, end, id))

    items = [0] * 12
    for d, e in cur.fetchall():
        items[int(d.month) - 1] += int(e)

    print(items)

    return make_response({
        'items': items,
    })


@app.route('/flow')
def show_flow():
    sql_flow = "SELECT flow_date, times FROM flow " \
               "WHERE flow_date between to_date(:1,'yyyy') and to_date(:2,'yyyy') " \
               "and hospital_id = :3"
    db = cx_Oracle.connect('admin/12345678@oracle-hims-warehouse.cpfsluvxtsqc.us-east-2.rds.amazonaws.com:1521/ORCL')
    cur = db.cursor()
    start = request.args['query_year']
    end = str(int(request.args['query_year']) + 1)
    id = request.args['hospital_id']
    cur.execute(sql_flow, (start, end, id))

    items = [0] * 12
    for d, t in cur.fetchall():
        items[int(d.month) - 1] += int(t)

    print(items)

    return make_response({
        'items': items,
    })


@app.route('/occupancy')
def show_occupancy():
    sql_occupancy = "SELECT occu_date, occupied_rm_num, total_rm FROM occupancy " \
                    "WHERE occu_date between to_date(:1,'yyyy-mm') and to_date(:2,'yyyy-mm') " \
                    "and hospital_id = :3"
    db = cx_Oracle.connect('admin/12345678@oracle-hims-warehouse.cpfsluvxtsqc.us-east-2.rds.amazonaws.com:1521/ORCL')
    cur = db.cursor()
    year = request.args['query_year']
    month = int(request.args['query_month'])
    start = year + "-" + str(month)
    end = year + "-" + str(month + 1)
    id = request.args['hospital_id']
    cur.execute(sql_occupancy, (start, end, id))

    occupiedData = [0] * 30
    totalData = [0] * 30
    for d, o, t in cur.fetchall():
        occupiedData[d.day - 1] += o
        totalData[d.day - 1] = t

    print(occupiedData, totalData)

    return make_response({
        'totalData': totalData,
        'occupiedData': occupiedData,
    })


if __name__ == '__main__':
    app.run(debug=True, port=8881)
