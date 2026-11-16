# app.py
from flask import Flask, render_template, request, jsonify
from model_utils import predict_price

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    error = None
    form_data = {} 

    if request.method == 'POST':
        try:
            # Сохраняем всё, что ввёл пользователь, чтобы вернуть обратно в форму
            form_data = {
                'area_sqft':           request.form.get('area_sqft', '1800'),
                'lot_size_sqft':       request.form.get('lot_size_sqft', '8000'),
                'beds_num':            request.form.get('beds_num', '3'),
                'baths_num':           request.form.get('baths_num', '2.0'),
                'stories_num':         request.form.get('stories_num', '1.5'),
                'property_age':        request.form.get('property_age', '30'),
                'school_rating_mean':  request.form.get('school_rating_mean', '6'),
                'zipcode':             request.form.get('zipcode', '77001'),
                'state':               request.form.get('state', 'TX'),
                'city':                request.form.get('city', 'houston'),
                'property_type_group': request.form.get('property_type_group', 'single_family'),
                'years_since_remodel': request.form.get('years_since_remodel', '0'),
                # чекбоксы: если не отмечено — поля нет в request.form
                'was_remodeled':       'was_remodeled' in request.form,
                'has_private_pool':    'has_private_pool' in request.form,
                'has_fireplace':       'has_fireplace' in request.form,
                'has_cooling':         'has_cooling' in request.form,
                'has_heating':         'has_heating' in request.form,
                'has_parking':         'has_parking' in request.form,
            }

            # Собираем input_dict для модели 
            input_dict = {
                'area_sqft':           float(form_data['area_sqft']),
                'beds_num':            int(form_data['beds_num']),
                'baths_num':           float(form_data['baths_num']),
                'stories_num':         float(form_data['stories_num']),
                'property_age':        int(form_data['property_age']),
                'lot_size_sqft':       float(form_data['lot_size_sqft']),
                'school_rating_mean':  float(form_data['school_rating_mean']),
                'was_remodeled':       int(form_data['was_remodeled']),
                'years_since_remodel': (
                    float(form_data['years_since_remodel'])
                    if form_data['was_remodeled'] else None
                ),
                'has_private_pool':    int(form_data['has_private_pool']),
                'has_fireplace':       int(form_data['has_fireplace']),
                'has_cooling':         int(form_data['has_cooling']),
                'has_heating':         int(form_data['has_heating']),
                'has_parking':         int(form_data['has_parking']),
                'zipcode':             form_data['zipcode'].strip(),
                'state':               form_data['state'],
                'city':                form_data['city'].strip().lower(),
                'property_type_group': form_data['property_type_group'],
            }
            prediction = predict_price(input_dict)

        except Exception as e:
            error = f"Ошибка при расчёте: {e}"

    return render_template('index.html', prediction=prediction, error=error, form=form_data)


@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json(force=True)
        price = predict_price(data)
        return jsonify({
            'status': 'ok',
            'predicted_price': price,
            'currency': 'USD'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)