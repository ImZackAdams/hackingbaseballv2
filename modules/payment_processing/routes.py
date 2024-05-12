from flask import render_template


@app.route('/success')
def success():
    # Render the success page with the user's results
    return render_template('results.html')

@app.route('/cancel')
def cancel():
    # Render the cancel page
    return render_template('cancel.html')