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
$result = New-Object PSObject;
Set-Attr $result "changed" $false;

$state = Get-Attr $params state -default 'present'
$name = Get-Attr $params name -failifempty $true -emptyattributefailmessage "Missing required argument: name"
$value = Get-Attr $params value -failifempty $true -emptyattributefailmessage "Missing required argument: value"
$separator = Get-Attr $params separator -default ';'
$level = Get-Attr $params level -default 'machine'

try{
	# Checking parameters
	if ('present','absent' -notcontains $state) {
		Fail-Json $result "state is $state; must be present or absent"
	} elseif ('machine','user' -notcontains $level) {
		Fail-Json $result "state is $level; must be machine or user"
	} elseif ([string]::IsNullOrEmpty($name)) {
		Fail-Json $result "Missing required argument: name"
	} elseif ([string]::IsNullOrEmpty($separator)) {
		Fail-Json $result "Missing required argument: separator"
	} elseif ([string]::IsNullOrEmpty($value)) {
		Fail-Json $result "Missing required argument: value"
	
	# Processing environment variable
	} else {
		$newValue = [Environment]::GetEnvironmentVariable($name, $level).Split($separator, [StringSplitOptions]::RemoveEmptyEntries)
		
		switch ($state){
			'present' {
				if($newValue -notcontains $value) {
					$newValue += $value
					$result.changed = $true
				}
			}
			'absent' {
				if($newValue -contains $value) {
					$newValue = $newValue | Where-Object { $_ -ne $value }
					$result.changed = $true
				}
			}
		}
		
		[Environment]::SetEnvironmentVariable($name, [string]::Join($separator, $newValue), $level)
	}
}
catch {
     Fail-Json $result $_.Exception.Message
}

Exit-Json $result;
