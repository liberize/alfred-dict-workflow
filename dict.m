#import <Foundation/Foundation.h>
#include <CoreServices/CoreServices.h>

NSUserDefaults* GetUserDefaults() {
    return [NSUserDefaults standardUserDefaults];
}

NSMutableDictionary* GetGlobalDomain() {
    NSUserDefaults *userDefaults = GetUserDefaults();
    NSMutableDictionary *dictionaryPrefs =
    [[userDefaults persistentDomainForName:@"Apple Global Domain"] mutableCopy];
    return dictionaryPrefs;
}

NSMutableDictionary* GetDictionaryPreferences() {
    return [[GetGlobalDomain() objectForKey:@"com.apple.DictionaryServices"] mutableCopy];
}

NSArray* GetCurrentDictionaryList() {
    return [GetDictionaryPreferences() objectForKey:@"DCSActiveDictionaries"];
}

void SetUserDictPreferences(NSArray* array) {
    NSMutableDictionary *currentPref = GetDictionaryPreferences();
    [currentPref setObject:array forKey:@"DCSActiveDictionaries"];
    NSDictionary *immutPref = [NSDictionary dictionaryWithDictionary:currentPref];
    NSMutableDictionary *g = GetGlobalDomain();
    [g setObject:immutPref forKey:@"com.apple.DictionaryServices"];
    NSUserDefaults *defaults = GetUserDefaults();
    [defaults setPersistentDomain:g forName:@"Apple Global Domain"];
}


int main(int argc, char *argv[]) {
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    
    NSArray *currentPrefs = GetCurrentDictionaryList();
    
    NSString *dict = [NSString stringWithUTF8String:argv[1]];
    NSString *word = [NSString stringWithUTF8String:argv[2]];
    SetUserDictPreferences([NSArray arrayWithObject:dict]);
    puts([(NSString *)DCSCopyTextDefinition(NULL, (CFStringRef)word,
                                            CFRangeMake(0, [word length])) UTF8String]);
    
    SetUserDictPreferences(currentPrefs);
}