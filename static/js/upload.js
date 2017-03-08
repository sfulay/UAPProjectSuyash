function uploadFile(blobFile, fileName) {
    var fd = new FormData();
    fd.append("fileToUpload", blobFile);

    $.ajax({
       url: "/uploadSQL",
       type: "POST",
       data: fd,
       processData: false,
       contentType: false,
       success: function(response) {
           // .. do something
       },
       error: function(jqXHR, textStatus, errorMessage) {
           console.log(errorMessage); // Optional
       }
    });
}  