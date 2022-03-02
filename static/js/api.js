$(function() {  //when a $ sign is used before a function, it becomes an event listener 
    $('#upload-file-btn').click(function() {
        var form_data = new FormData($('#upload-file')[0]);
        
        $.ajax({
            type: 'POST',
            url: '/resultpage',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                console.log('Success!');
                console.log(data);

                if(data.recognised){
                document.getElementById('response-name').innerHTML = data.payload.name; // used to access an element by its id
                //document.getElementById('response-value').innerHTML = (data.analysis.value.toFixed(2) * 100) + "%";
                document.getElementById('response-value').innerHTML = parseInt(data.payload.value * 10000)/100 + "%";
                }
                else {
                    document.getElementById('response-name').innerHTML = "Not recognised";
                    document.getElementById('response-value').innerHTML = null;
                }
                
            },
        });
    });
});