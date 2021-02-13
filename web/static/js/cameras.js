$(document).ready(function() {
    function UpdateCameras() {
        $.ajax({
            "url": "/api/cam_info"
        })
        .done(function(res) {
            cams = JSON.parse(res);
            console.log(cams);

            cams.forEach(cam => {
                let cam_card = $("#cam-"+cam.id);
                let cam_img = cam_card.find('.camera-img');
                let cam_status = cam_card.find('.status');
                cam_status.text("Status: " + (cam.connected ? "Connected" : "Not Connected"));

                if (cam.connected) {
                    let src = cam_img.data('default-src');
                    let rand = Math.floor(Math.random() * 100).toString();
                    cam_img.prop('src', src+"?t="+rand);
                }
                else {
                    cam_img.prop('src', 'static/images/not_connected.jpg');
                }
            });
        });
    }

    setInterval(UpdateCameras, 5000);
    UpdateCameras();
});