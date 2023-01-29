let result = document.querySelector('.result'),
  img_result = document.querySelector('.circle'),
  options = document.querySelector('.options'),
  save_photo = document.querySelector('#save-photo'),
  save_profile = document.querySelector('#save-profile'),
  cropped = document.querySelector('.profile-pic'),
  updated = document.querySelector('.updated-profile'),
  remove = document.querySelector('.remove-profile'),
  upload = document.querySelector('#agent-profile-input'),
  svg = document.querySelector('.profile-svg');
upadted_svg = document.querySelector('.updated-svg');
remove_profile_svg = document.querySelector('.remove-profile-svg');
remove_btn = document.querySelector('#remove-profile-btn');
cropper = '';
var imgx;

function hasExtension(inputID, exts) {
  var fileName = document.getElementById(inputID).value;
  return (new RegExp('(' + exts.join('|').replace(/\./g, '\\.') + ')$')).test(fileName);
}

// on change show image with crop options
var agent_profile_input_file_global = undefined;
upload.addEventListener('change', (e) => {
  hide_agent_profile_errors();
  if (e.target.files.length) {
    if (!hasExtension('agent-profile-input', ['.jpg', '.jpeg', '.png'])) {
      $('#agent-profile-input').val('');
      show_agent_profile_errors("* File format is not supported. Please upload .jpg .jpeg or .png file.");
      return false;
    }

    agent_profile_input_file_global = ($("#agent-profile-input"))[0].files[0];

    if (agent_profile_input_file_global.size / 1000000 >= 1) {
      show_agent_profile_errors("File size cannot exceed 1 MB");
      return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
      if (await check_for_malicious_agent_profile_picture(e.target.result)) {
        $('#preview-profile-pic-Modal').modal('hide');
        $('#upload-profile-pic-Modal').modal('show');
        document.querySelector('.updated-profile').src = "";
        $(".updated-svg").addClass("show");
        $('#agent-profile-input').val('');
        show_agent_profile_errors("Your uploaded file is corrupted.");
      } else if (e.target.result) {
        $('#preview-profile-pic-Modal').modal('show');
        $('#upload-profile-pic-Modal').modal('hide');
        // create new image
        let img = document.createElement('img');
        img.id = 'image';
        img.src = e.target.result
        // clean result before
        result.innerHTML = '';
        // append new image
        result.appendChild(img);
        // init cropper
        cropper = new Cropper(img, {
          aspectRatio: 16 / 16,
          viewMode: 0,
          dragMode: 'none',
          movable: false,
          minContainerWidth: 200,
          minContainerHeight: 200,
          rotatable: true,

        });

      }
    };
    document.querySelector(".remove-btn").disabled = false;
    document.querySelector(".remove-btn").style.opacity = 1;
    reader.readAsDataURL(e.target.files[0]);
    $('#agent-profile-input').val('');
  }
});

$('#rotate-image').click(function () {
  cropper.rotate(90);
});

// save on click
save_photo.addEventListener('click', (e) => {
  e.preventDefault();
  $('#upload-profile-pic-Modal').modal('show');
  $('#preview-profile-pic-Modal').modal('hide');
  let imgSrc = cropper.getCroppedCanvas().toDataURL();
  // upadted_svg.classList.add('hide');
  $('.updated-svg').addClass("hide");
  updated.src = imgSrc;
});

save_profile.addEventListener('click', (e) => {
  e.preventDefault();
  if (agent_profile_input_file_global != undefined) {
    let imgSrc = cropper.getCroppedCanvas().toDataURL();
    $('.profile-svg').removeClass("hide");
    cropped.src = imgSrc;
  }

})

remove_btn.addEventListener('click', (e) => {
  cropped.src = '';
  updated.src = '';
  remove.src = '';
  $('.profile-svg').removeClass("hide");
  // svg.classList.remove('hide');
  upadted_svg.classList.remove('hide');
  $('#agent-profile-input').val('');
})