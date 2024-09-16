function success_failed_handler(status_message,element,error_success_element,message){
  if(status_message == 'success'){
    document.getElementById(element).className = 'form-control is-valid';
    document.getElementById(error_success_element).className = 'form-text text-success';
    document.getElementById(error_success_element).innerHTML = message;                
  }
  else if (status_message == 'failed'){
    document.getElementById(element).className = 'form-control is-invalid';
    document.getElementById(error_success_element).className = 'form-text text-danger';  
    document.getElementById(error_success_element).innerHTML = message;              
  }
}