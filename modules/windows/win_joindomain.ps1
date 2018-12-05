#!powershell
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# WANT_JSON
# POWERSHELL_COMMON

$params = Parse-Args $args;

$domain = Get-Attr $params "domain" -failifempty $true
$user = Get-Attr $params "user" -failifempty $true
$pass = Get-Attr $params "pass" -failifempty $true
$ou = Get-Attr $params "ou" -failifempty $false
$state = Get-Attr $params "state"  -default 'present'

$result = New-Object PSObject;
Set-Attr $result "changed" $false;

try{

	# Checking parameters
	if ('present','absent' -notcontains $state) {
		Fail-Json $result "state is $state; must be present or absent"
	}

	$computerdomain = (Get-WmiObject win32_computersystem).Domain
	if ($computerdomain -notlike "$domain*" -and $domain -notlike "$computerdomain*") {
		try{
			$pass = ConvertTo-SecureString -String $pass -AsPlainText -Force
			$cred = New-Object System.Management.Automation.PSCredential($user, $pass) 
			
			switch ($state){
				'present' {
					if($ou) {
						Add-Computer -DomainName $domain -Credential $cred -OUPath $ou
					}
					else {
						Add-Computer -DomainName $domain -Credential $cred
					}
				}
				'absent' {
					#Remove-Computer -Credential $cred -PassRhru -Verbose
				}
			}
			
			
			
			$result.changed = $true
		}
		catch {
			 Fail-Json $result $_.Exception.Message
		}
	}
}
catch {
     Fail-Json $result $_.Exception.Message
}

Exit-Json $result;
