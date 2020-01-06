from flask import Blueprint, jsonify, current_app, render_template


bp = Blueprint('test', __name__)

@bp.route('/')
def index():
    rules_iterator = current_app.url_map.iter_rules()
    return jsonify(
        {rule.endpoint: rule.rule for rule in rules_iterator if rule.endpoint not in ('route_map', 'static')})


@bp.route('/test')
def test():
    return render_template('test.html')