function password_criteria(password_to_check){
  let pattern_A = /[A-Z]/g;
  let pattern_a = /[a-z]/g;
  let pattern_0 = /[0-9]/g;
  var result_A = password_to_check.match(pattern_A);
  var result_a = password_to_check.match(pattern_a);
  var result_0 = password_to_check.match(pattern_0);
  if (password_to_check.length >=8 && result_A && result_a && result_0){
    return true;
  }
  else{
    return false;
  }
}