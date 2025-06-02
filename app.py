from flask import Flask, jsonify, render_template,request,redirect,url_for
import json

import os

app = Flask(__name__)
from datetime import datetime,timedelta

def remove_exBus():
    if not os.path.exists('base.json'):
        return
    with open('base.json') as file:
          exBus=json.load(file)
    now=datetime.now()
    updated_bus=[]
    for ex in exBus:
        bus_datetime_str=f"{ex['date']} {ex['time']}"
        try:
              bus_datetime=datetime.strptime(bus_datetime_str, "%Y-%m-%d %H:%M")
              if bus_datetime + timedelta(minutes=1)> now:
                  updated_bus.append(ex)
        except Exception as e:
               updated_bus.append(ex)
    with open('base.json', 'w') as f:
        json.dump(updated_bus, f, indent=4)

@app.route('/')
def index():
    remove_exBus()
    return render_template('index.html')
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/add_bus', methods=['POST'])
def add_buses():
    print(request.form)
    bus={
        "company_name":request.form['company_name'],
        "from":request.form['from'],
        "to":request.form['to'],
        "time":request.form['time'],
        "date":request.form['date'],
        "price":request.form['price'],
        "plate_id":request.form['plate_id'],
        "seats":request.form['seats'],
        "ready":True
    }
    
    if os.path.exists('base.json'):
        with open('base.json') as file:
            try:
                buses = json.load(file)
            except:
                buses=[]
    else:
       buses = []
    buses.append(bus)
    with open('base.json', 'w') as f:
        json.dump(buses, f, indent=4)
    return redirect(url_for('index'))

@app.route('/get_buses')
def get_buses():
    remove_exBus()
    with open('base.json') as f:
        data = json.load(f)
    return jsonify(data)
@app.route('/book/<plate_id>')
def book_page(plate_id):
    bus=None
    if os.path.exists('base.json'):
        with open('base.json') as file:
            buses=json.load(file)
            for b in buses:
                if b['plate_id']==plate_id:
                    bus=b
                    break
    return render_template('book.html',bus=bus)
@app.route('/book/<plate_id>', methods=['POST'])
def book_seats(plate_id):
    data=request.get_json()
    count=int(data.get('count',1))
    updated_buses=[]
    seat_booked=False
    seats_left=None
    if os.path.exists('base.json'):
        with open('base.json') as file:
            buses=json.load(file)
    else:
            return jsonify({"success":False,"message":"No buses available"}), 400
    
    for b in buses:
                if b['plate_id']==plate_id:
                    seats_left=int(b['seats'])-count
                    if seats_left>=0:
                        b['seats']=seats_left
                        seat_booked=True
                    updated_buses.append(b)
                else:
                    updated_buses.append(b)
    with open('base.json', 'w') as f:
                json.dump(updated_buses, f, indent=4)
    if seat_booked:
        return jsonify({"success":True,"seats_left":seats_left,"message":"Seats booked successfully"})   
    else:
        return jsonify({"success":False,"message":"Not enough seats available or bus not found"}), 400


          
if __name__ == '__main__':
    app.run(port=8000,debug=True)

