use CGI::Cookie;
use Digest::SHA1 qw(sha1_hex);
sub get_uid(){
  # this returns the uid from the cookie, or 0 if no valid cookie
  # optional parameter: $matchcode,  then function returns uid if client subscribes
  my $matchcode=$_[0];
  my %cookies = CGI::Cookie->fetch();

  if ($cookies{user} && $cookies{auth}) {
    $username=$cookies{user}->value; 
    my $sth=$dbh->prepare("select uid,token from usagepasswd where email='$username'");
    
    #print p, "select uid,token from passwd where username='$username'";
    $sth->execute();
    my ($uid,$token)=$sth->fetchrow();
    
    my $auth_string = sha1_hex($cookies{user}->value . ":" . $token);
    #  print p, $cookies{user}, p, $cookies{auth}, p, $auth_string;
    #}
    
    #print p, $auth_string,p,$cookies{auth}->value;
    
    if ($auth_string eq $cookies{auth}->value){
      return $uid;
    }
    else {
      return 0;
    }
  } 
  else {
    return 0;
  }
}
1;