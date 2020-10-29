from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, TextAreaField, SelectField, DateField, HiddenField, IntegerField, ValidationError, PasswordField
from wtforms.validators import Length, Email, InputRequired
from wtforms.fields.html5 import DateField
# from wtforms_components import PhoneNumberField

import phonenumbers

# # Form ORM
class UserForm(FlaskForm):    
        name = TextField(' Name :   ', validators=[InputRequired(),Length(max=50)] )
        email = TextField(' Email :   ', validators=[Email(), InputRequired(), ])
        phone = TextField('Phone :   ', validators=[InputRequired()])
        exam = SelectField('Exam :   ', choices = [('0', 'STEP 1'), ('1', 'STEP 2'), ('2', 'STEP 3')])
        dates = TextField('DatePicker : ', validators=[InputRequired()])
        country = SelectField('Country : ', choices = [('AFGHANISTAN' , 'AFGHANISTAN'), ('UNITED ARAB EMIRATES' , 'UNITED ARAB EMIRATES'), ('ARGENTINA' , 'ARGENTINA'), ('ARGENTINA' , 'ARGENTINA'), ('ARMENIA' , 'ARMENIA'), ('AMERICAN SAMOA' , 'AMERICAN SAMOA'), ('AUSTRALIA' , 'AUSTRALIA'), ('BANGLADESH' , 'BANGLADESH'), ('BOLIVIA' , 'BOLIVIA'), ('BRAZIL' , 'BRAZIL'), ('CANADA' , 'CANADA'), ('SWITZERLAND' , 'SWITZERLAND'), ('CHILE' , 'CHILE'), ('CHINA' , 'CHINA'), ('COLOMBIA' , 'COLOMBIA'), ('COSTA RICA' , 'COSTA RICA'), ('CYPRUS' , 'CYPRUS'), ('CZECH REPUBLIC' , 'CZECH REPUBLIC'), ('GERMANY' , 'GERMANY'), ('DENMARK' , 'DENMARK'), ('DOMINICAN REPUBLIC' , 'DOMINICAN REPUBLIC'), ('EGYPT' , 'EGYPT'), ('SPAIN' , 'SPAIN'), ('FINLAND' , 'FINLAND'), ('FRANCE' , 'FRANCE'), ('UNITED KINGDOM' , 'UNITED KINGDOM'), ('GHANA' , 'GHANA'), ('GREECE' , 'GREECE'), ('GUATEMALA' , 'GUATEMALA'), ('GUAM' , 'GUAM'), ('HONG KONG' , 'HONG KONG'), ('HONG KONG' , 'HONG KONG'), ('CROATIA' , 'CROATIA'), ('CROATIA' , 'CROATIA'), ('HUNGARY' , 'HUNGARY'), ('INDONESIA' , 'INDONESIA'), ('INDIA' , 'INDIA'), ('IRELAND' , 'IRELAND'), ('ISRAEL' , 'ISRAEL'), ('ITALY' , 'ITALY'), ('JORDAN' , 'JORDAN'), ('JAPAN' , 'JAPAN'), ('KENYA' , 'KENYA'), (' KOREA REPUBLIC OF' , ' KOREA REPUBLIC OF'), ('KUWAIT' , 'KUWAIT'), ('LEBANON' , 'LEBANON'), ('SRI LANKA' , 'SRI LANKA'), ('LITHUANIA' , 'LITHUANIA'), ('MEXICO' , 'MEXICO'), ('NORTHERN MARIANA ISLANDS' , 'NORTHERN MARIANA ISLANDS'), ('MAURITIUS' , 'MAURITIUS'), ('MALAYSIA' , 'MALAYSIA'), ('NETHERLANDS' , 'NETHERLANDS'), ('NEPAL' , 'NEPAL'), ('NEW ZEALAND' , 'NEW ZEALAND'), ('OMAN' , 'OMAN'), ('PAKISTAN' , 'PAKISTAN'), ('PERU' , 'PERU'), ('PHILIPPINES' , 'PHILIPPINES'), ('PUERTO RICO' , 'PUERTO RICO'), ('PORTUGAL' , 'PORTUGAL'), ('QATAR' , 'QATAR'), ('SAUDI ARABIA' , 'SAUDI ARABIA'), ('SINGAPORE' , 'SINGAPORE'), ('THAILAND' , 'THAILAND'), ('TRINIDAD AND TOBAGO' , 'TRINIDAD AND TOBAGO'), ('TURKEY' , 'TURKEY'), ('TAIWAN' , 'TAIWAN'), ('UGANDA' , 'UGANDA'), ('UNITED STATES' , 'UNITED STATES'), ('VENEZUELA' , 'VENEZUELA'), ('VIRGIN ISLANDS (U.S.)' , 'VIRGIN ISLANDS (U.S.)'), ('SOUTH AFRICA' , 'SOUTH AFRICA'), ('ZIMBABWE' , 'ZIMBABWE')])
        submit = SubmitField('Submit')
        id = HiddenField('id')

        locations = []
        orig_email = HiddenField("Original Email")

        def validate_phone(self, phone):
                try:
                        p = phonenumbers.parse(phone.data)
                        if not phonenumbers.is_valid_number(p):
                                raise ValueError()
                except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
                        raise ValidationError('Invalid phone number')

class LoginForm(FlaskForm):    
        name = TextField(' Name :   ', validators=[InputRequired(),Length(max=20)] )
        password = PasswordField(' Password :   ', validators=[InputRequired(),Length(max=20)] )
        submit = SubmitField('Log in')  
        

# class UserForm(ModelForm):
#     class Meta:
#         model = User
#         validators = {'name': [InputRequired()], 'email': [InputRequired(), Email()], 'phone': [InputRequired()]}


