def is_palindrome(s):
 s=str(s)
 l=len(s)
 c=0
 while c<=l/2:
  if s[c]!=s[l-c-1]:
   return False
  c+=1
 return True

print(is_palindrome("aabbaa"))