function EventTracker() {
	this.log = function(data) {
		fetch('http://127.0.0.1:5001/analytics/', {
			method: 'post',
			body: JSON.stringify(data)
		});
	};
}

tracker = new EventTracker();
tracker.log({'event1':'val1', 'event2':'val2'});
