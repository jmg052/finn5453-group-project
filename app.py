import portfolio_analyzer  # Ensure this import is correctly set up
from flask_weasyprint import HTML, render_pdf
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__, template_folder='templates')

def calculate_investor_profile(data):
    score_map = {"low": 1, "medium": 2, "high": 3}
    scores = []
    min_risk_tolerance = float('inf')

    for i in range(3):  # Since there are 3 users
        user_scores = [score_map.get(data[f'{field}{i+1}'], 1) for field in ['investment_horizon', 'risk_profile', 'liquidity_needs', 'income_level', 'market_confidence']]
        user_total = sum(user_scores)
        scores.append(user_total)
        min_risk_tolerance = min(min_risk_tolerance, user_scores[1])  # Assuming risk_profile is the second field

    avg_score = sum(scores) / len(scores)

    # Custom Logic considering the minimum risk tolerance
    if min_risk_tolerance == 1 or avg_score <= 8:
        return "conservative"
    elif 8 < avg_score <= 12:
        return "moderate"
    else:
        return "aggressive"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_data = {}
        for field in ['investment_horizon', 'risk_profile', 'liquidity_needs', 'income_level', 'market_confidence']:
            for i in range(1, 4):
                form_data[f'{field}{i}'] = request.form.get(f'{field}{i}')

        profile_type = calculate_investor_profile(form_data)
        # Redirect to the results page with the profile type as a query parameter
        return redirect(url_for('view_results', profile_type=profile_type))

    return render_template('questionnaire.html')

@app.route('/results')
def view_results():
    profile_type = request.args.get('profile_type')
    if not profile_type:
        return redirect(url_for('index'))

    results = portfolio_analyzer.calculate_portfolio_performance(profile_type)
    return render_template('results.html', profile_type=profile_type, results=results)

@app.route('/results/pdf')
def results_pdf():
    profile_type = request.args.get('profile_type')
    if not profile_type:
        return redirect(url_for('index'))

    results = portfolio_analyzer.calculate_portfolio_performance(profile_type)
    html = render_template('results.html', profile_type=profile_type, results=results)
    return render_pdf(HTML(string=html))

if __name__ == '__main__':
    app.run(debug=False, threaded=True)
