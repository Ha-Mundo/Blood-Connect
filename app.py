"""
TODO 
add pagination
improve ui
"""

from flask import Flask, request, jsonify, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, func, Column, Date, Integer, Text, asc, desc
from sqlalchemy.orm import sessionmaker
from time_limit import threshold_donation, threshold_request, timer, donation_day
import datetime

file_name = 'BloodDonationSystem.db'
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{file_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)

class BloodDonation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    blood_groups = db.Column(db.String, nullable=False)
    city = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    latest_donation = db.Column(db.Date, nullable=False)
    next_donation = db.Column(db.Date)
    donation_counter = db.Column(db.Integer, default=1)


    def __init__(self, name, age, blood_groups, city, email, latest_donation, next_donation, donation_counter):
        self.name = name
        self.age = age
        self.blood_groups = blood_groups
        self.city = city
        self.email = email
        self.latest_donation = latest_donation
        self.next_donation = next_donation
        self.donation_counter = donation_counter
        
class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable=False)
    blood_groups = db.Column(db.String, nullable=False)
    city = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    latest_request = db.Column(db.Date, nullable=False)
    next_request = db.Column(db.Date)
    request_counter = db.Column(db.Integer, default=1)


    def __init__(self, name, blood_groups, city, email, latest_request, next_request, request_counter):
        self.name = name
        self.blood_groups = blood_groups
        self.city = city
        self.email = email
        self.latest_request = latest_request
        self.next_request = next_request
        self.request_counter = request_counter


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/empty_db')
def no_donations():
    return render_template('empty_db.html')

@app.route('/blood_donation', methods=['GET','POST'])
def blood_donation():
    if request.method == 'GET':
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        return render_template('donate.html', blood_groups = blood_groups)
    else:
        donation_day = datetime.date.today()
        next_donation_date = threshold_donation(donation_day)
        
        data_fields = ['name','age','blood_groups','city','email']
    
        data_dict = {}
        data_dict['latest_donation'] = donation_day
        data_dict['next_donation'] = next_donation_date
                      
    
        for field in data_fields:
            data_dict[field] = request.form.get(field).lower()

        for value in data_dict.values():
            if value == "":
                return "Please enter all the details." 
                  
        counter = db.session.query(BloodDonation).filter(BloodDonation.email == data_dict['email']).count() 
        next_bd = db.session.query(BloodDonation).filter(BloodDonation.next_donation).count() 
                
        if counter == 0:
            counter += 1
            data_dict['donation_counter'] = counter
            blood_donation = BloodDonation(**data_dict)
            db.session.add(blood_donation)
            db.session.commit()
            flash(f"Thank you {blood_donation.name[0].upper()}{blood_donation.name[1:]} for your availability. We'll get in touch soon!", "success")
            return redirect(url_for('home')) 
          
        elif next_bd > 0:
            query = db.session.query(BloodDonation.next_donation).filter(BloodDonation.email == data_dict['email']).all()
            next_bd_date = list(query[::-1][0])
            
            if next_bd_date[0] <= donation_day:   
                counter += 1
                data_dict['donation_counter'] = counter
                blood_donation = BloodDonation(**data_dict)
                db.session.add(blood_donation)
                db.session.commit()
                flash(f"Thank you {blood_donation.name[0].upper()}{blood_donation.name[1:]} for your availability. We'll get in touch soon!", "success")
                return redirect(url_for('home')) 
            
            else:
                flash("Donation forbidden! Only one blood donation every 3 months is allowed.", "danger")   
                return redirect(url_for('blood_donation')) 
          
         
        else:    
            flash("Donation forbidden! Only one blood donation every 3 months is allowed.", "danger")   
            return redirect(url_for('blood_donation')) 

@app.route('/blood_receive', methods=['GET','POST'])
def blood_receive():
    if request.method == 'GET':

        all_donations = BloodDonation.query.all()
        if all_donations == []:
            print('Sorry no donations available')
            return render_template('empty_db.html')

        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        return render_template('find_blood.html', blood_groups = blood_groups)

    else:
        blood_groups = request.form.get('blood_groups').lower()
        city = request.form.get('city').lower()
        name = request.form.get('name').lower()
        email = request.form.get('email').lower()
        
        if city == "":
            return "Please enter all the details." 
        
        next_request_date = threshold_request(donation_day)
        receiver_fields = ['blood_groups','city','name','email']
    
        request_dict = {}
        request_dict['latest_request'] = donation_day
        request_dict['next_request'] = next_request_date
        
        for field in receiver_fields:
            request_dict[field] = request.form.get(field).lower()
            
        counter = db.session.query(BloodRequest).filter(BloodRequest.email == request_dict['email']).count() 
        next_br = db.session.query(BloodRequest).filter(BloodRequest.next_request).count()
        
        if counter == 0:
            counter += 1
            request_dict['request_counter'] = counter
            blood_request = BloodRequest(**request_dict)
            db.session.add(blood_request)
            db.session.commit()
           
        elif next_br > 0:
            query = db.session.query(BloodRequest.next_request).filter(BloodRequest.email == request_dict['email']).all()
            next_br_date = list(query[::-1][0])
            
            if next_br_date[0] <= donation_day:   
                counter += 1
                request_dict['request_counter'] = counter
                blood_request = BloodRequest(**request_dict)
                db.session.add(blood_request)
                db.session.commit()
                
            else:
                flash("Request Forbidden! Is allowed only one blood request per week", "danger")   
                return redirect(url_for('blood_receive')) 
            
        else:
            flash("Request Forbidden!!! Is allowed only one blood request per week", "danger")   
            return redirect(url_for('blood_receive'))  
    
   
        print(city, blood_groups)
        result = BloodDonation.query\
            .filter_by(blood_groups = blood_groups)\
            .filter_by(city = city)\
            .all()
                
        total_result = BloodDonation.query\
            .filter_by(blood_groups = blood_groups)\
            .filter_by(city = city)\
            .count()
        
        if result == []:
            print('Sorry no donations available')
            return render_template('empty_db.html')
        else:
            return render_template('results.html', blood_donations=result, city=city, total_result = total_result)
        
    print(result)
    return render_template('results.html', blood_donations=result)

@app.route('/take_donation')
def take_donation():
    blood_donation_id = request.args.get('id')
    request_name = BloodRequest.query.order_by(BloodRequest.id.desc()).first()
    result = BloodDonation.query.get(blood_donation_id)
    print(result)
    db.session.delete(result)
    db.session.commit()
    flash(f"Thank you {request_name.name[0].upper()}{request_name.name[1:]} for your request! We let you know as soon as possible!", "success")
    return redirect(url_for('home'))

@app.route('/all_donations_db', methods=['GET'] )
def all_donations_db():
    all_donations = BloodDonation.query.all()[::-1]
    all_donations_counter = BloodDonation.query.count()
    return render_template('blood_db.html', blood_donations=all_donations, all_donations_counter = all_donations_counter)

if __name__ == '__main__':
    app.run(debug=True)