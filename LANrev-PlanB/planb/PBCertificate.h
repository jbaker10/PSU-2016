/*

 Plan B
 PBCertificate.h

 This file is forked from Santa's SNTCertificate.h.
 
 Copyright 2014 Google Inc.

 Licensed under the Apache License, Version 2.0 (the "License"); you may not
 use this file except in compliance with the License.  You may obtain a copy
 of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
 License for the specific language governing permissions and limitations under
 the License.

*/

/// PBCertificate wraps a @c SecCertificateRef to provide Objective-C accessors to
/// commonly used certificate data. Accessors cache data for repeated access.
@interface PBCertificate : NSObject<NSSecureCoding>

/// Access the underlying certificate ref.
@property(readonly) SecCertificateRef certRef;

/// SHA-1 hash of the certificate data.
@property(readonly) NSString *SHA1;

/// Certificate data.
@property(readonly) NSData *certData;

/// Common Name e.g: "Software Signing".
@property(readonly) NSString *commonName;

/// Country Name e.g: "US".
@property(readonly) NSString *countryName;

/// Organizational Name e.g: "Apple Inc".
@property(readonly) NSString *orgName;

/// Organizational Unit Name e.g: "Apple Software".
@property(readonly) NSString *orgUnit;

/// Issuer details, same fields as above.
@property(readonly) NSString *issuerCommonName;
@property(readonly) NSString *issuerCountryName;
@property(readonly) NSString *issuerOrgName;
@property(readonly) NSString *issuerOrgUnit;

/// Validity Not Before.
@property(readonly) NSDate *validFrom;

/// Validity Not After.
@property(readonly) NSDate *validUntil;

/// Initialize a PBCertificate object with a valid SecCertificateRef. Designated initializer.
- (instancetype)initWithSecCertificateRef:(SecCertificateRef)certRef;

/// Initialize a PBCertificate object with certificate data in DER format.
/// Returns nil if |certData| is invalid.
- (instancetype)initWithCertificateDataDER:(NSData *)certData;

/// Initialize a PBCertificate object with certificate data in PEM format.
/// If multiple PEM certificates exist within the string, the first is used.
/// Returns nil if |certData| is invalid.
- (instancetype)initWithCertificateDataPEM:(NSString *)certData;

/// Returns an array of PBCertificate's for all of the certificates in |pemData|.
+ (NSArray *)certificatesFromPEM:(NSString *)pemData;

@end
