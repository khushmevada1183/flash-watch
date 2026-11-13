import UIKit
import Capacitor
import HealthKit

@objc(ViewController)
class ViewController: CAPBridgeViewController {
    override open func capacitorDidLoad() {
        super.capacitorDidLoad()
        bridge?.registerPluginInstance(HealthKitPlugin())
    }
}

@objc(HealthKitPlugin)
public class HealthKitPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "HealthKitPlugin"
    public let jsName = "HealthKit"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "isAvailable", returnType: "promise"),
        CAPPluginMethod(name: "requestAuthorization", returnType: "promise"),
        CAPPluginMethod(name: "saveSportRecord", returnType: "promise"),
        CAPPluginMethod(name: "saveSportRecords", returnType: "promise"),
        CAPPluginMethod(name: "getTodaySteps", returnType: "promise"),
        CAPPluginMethod(name: "openShortcutSync", returnType: "promise"),
        CAPPluginMethod(name: "openShortcutsApp", returnType: "promise")
    ]

    private let healthStore = HKHealthStore()

    @objc func isAvailable(_ call: CAPPluginCall) {
        call.resolve([
            "available": HKHealthStore.isHealthDataAvailable()
        ])
    }

    @objc func requestAuthorization(_ call: CAPPluginCall) {
        guard HKHealthStore.isHealthDataAvailable() else {
            call.reject("HealthKit is not available on this device")
            return
        }

        guard let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount),
              let distType = HKQuantityType.quantityType(forIdentifier: .distanceWalkingRunning),
              let calType = HKQuantityType.quantityType(forIdentifier: .activeEnergyBurned) else {
            call.reject("Unable to initialize HealthKit data types")
            return
        }

        let writeTypes: Set<HKSampleType> = [stepType, distType, calType]
        let readTypes: Set<HKObjectType> = [stepType, distType, calType]

        healthStore.requestAuthorization(toShare: writeTypes, read: readTypes) { success, error in
            if let error = error {
                let desc = error.localizedDescription
                if desc.contains("entitlement") || (error as NSError).code == 4 {
                    call.resolve([
                        "authorized": false,
                        "entitlementMissing": true,
                        "message": "Personal Apple ID sideloading does not have HealthKit entitlement. Local fitness vault is enabled."
                    ])
                    return
                }
                call.reject("HealthKit authorization failed: \(desc)")
            } else {
                call.resolve(["authorized": success, "entitlementMissing": false])
            }
        }
    }

    @objc func saveSportRecord(_ call: CAPPluginCall) {
        guard HKHealthStore.isHealthDataAvailable() else {
            call.reject("HealthKit is not available")
            return
        }

        guard let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount),
              let distType = HKQuantityType.quantityType(forIdentifier: .distanceWalkingRunning),
              let calType = HKQuantityType.quantityType(forIdentifier: .activeEnergyBurned) else {
            call.reject("HealthKit quantity types not found")
            return
        }

        let steps = call.getInt("steps") ?? 0
        let distance = call.getDouble("distance") ?? 0.0 // meters
        let calories = call.getDouble("calories") ?? 0.0 // kcal
        let duration = max(call.getDouble("duration") ?? 60.0, 1.0) // seconds
        let startTimeSec = call.getDouble("startTime") ?? Date().timeIntervalSince1970

        let startDate = Date(timeIntervalSince1970: startTimeSec)
        let endDate = startDate.addingTimeInterval(duration)

        let device = HKDevice(
            name: "boAt FLASH",
            manufacturer: "boAt",
            model: "FLASH",
            hardwareVersion: nil,
            firmwareVersion: nil,
            softwareVersion: "1.0",
            localIdentifier: nil,
            udiDeviceIdentifier: nil
        )

        let syncId = "boat-flash-\(Int(startTimeSec))"
        let metadata: [String: Any] = [
            HKMetadataKeyDeviceManufacturerName: "boAt",
            HKMetadataKeySyncIdentifier: syncId,
            HKMetadataKeySyncVersion: 1
        ]

        var samples: [HKSample] = []

        if steps > 0 {
            let stepQuantity = HKQuantity(unit: .count(), doubleValue: Double(steps))
            let stepSample = HKQuantitySample(type: stepType, quantity: stepQuantity, start: startDate, end: endDate, device: device, metadata: metadata)
            samples.append(stepSample)
        }

        if distance > 0 {
            let distQuantity = HKQuantity(unit: .meter(), doubleValue: distance)
            let distSample = HKQuantitySample(type: distType, quantity: distQuantity, start: startDate, end: endDate, device: device, metadata: metadata)
            samples.append(distSample)
        }

        if calories > 0 {
            let calQuantity = HKQuantity(unit: .kilocalorie(), doubleValue: calories)
            let calSample = HKQuantitySample(type: calType, quantity: calQuantity, start: startDate, end: endDate, device: device, metadata: metadata)
            samples.append(calSample)
        }

        guard !samples.isEmpty else {
            call.resolve(["saved": true, "sampleCount": 0])
            return
        }

        healthStore.save(samples) { success, error in
            if let error = error {
                let desc = error.localizedDescription
                if desc.contains("entitlement") || (error as NSError).code == 4 {
                    call.resolve([
                        "saved": false,
                        "entitlementMissing": true,
                        "sampleCount": samples.count,
                        "message": "HealthKit entitlement missing in provisioning profile. Stored to local fitness matrix."
                    ])
                    return
                }
                call.reject("Failed to save sport sample to HealthKit: \(desc)")
            } else {
                call.resolve([
                    "saved": success,
                    "sampleCount": samples.count
                ])
            }
        }
    }

    @objc func saveSportRecords(_ call: CAPPluginCall) {
        guard HKHealthStore.isHealthDataAvailable() else {
            call.reject("HealthKit is not available")
            return
        }

        guard let records = call.getArray("records", [String: Any].self), !records.isEmpty else {
            call.resolve(["saved": true, "sampleCount": 0])
            return
        }

        guard let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount),
              let distType = HKQuantityType.quantityType(forIdentifier: .distanceWalkingRunning),
              let calType = HKQuantityType.quantityType(forIdentifier: .activeEnergyBurned) else {
            call.reject("HealthKit quantity types not found")
            return
        }

        let device = HKDevice(
            name: "boAt FLASH",
            manufacturer: "boAt",
            model: "FLASH",
            hardwareVersion: nil,
            firmwareVersion: nil,
            softwareVersion: "1.0",
            localIdentifier: nil,
            udiDeviceIdentifier: nil
        )

        var samples: [HKSample] = []

        for item in records {
            let steps = item["steps"] as? Int ?? 0
            let distance = (item["distance"] as? NSNumber)?.doubleValue ?? 0.0
            let calories = (item["calories"] as? NSNumber)?.doubleValue ?? 0.0
            let duration = max((item["duration"] as? NSNumber)?.doubleValue ?? 60.0, 1.0)
            let startTimeSec = (item["startTime"] as? NSNumber)?.doubleValue ?? Date().timeIntervalSince1970

            let startDate = Date(timeIntervalSince1970: startTimeSec)
            let endDate = startDate.addingTimeInterval(duration)
            let syncId = "boat-flash-\(Int(startTimeSec))"
            let metadata: [String: Any] = [
                HKMetadataKeyDeviceManufacturerName: "boAt",
                HKMetadataKeySyncIdentifier: syncId,
                HKMetadataKeySyncVersion: 1
            ]

            if steps > 0 {
                let stepQuantity = HKQuantity(unit: .count(), doubleValue: Double(steps))
                samples.append(HKQuantitySample(type: stepType, quantity: stepQuantity, start: startDate, end: endDate, device: device, metadata: metadata))
            }
            if distance > 0 {
                let distQuantity = HKQuantity(unit: .meter(), doubleValue: distance)
                samples.append(HKQuantitySample(type: distType, quantity: distQuantity, start: startDate, end: endDate, device: device, metadata: metadata))
            }
            if calories > 0 {
                let calQuantity = HKQuantity(unit: .kilocalorie(), doubleValue: calories)
                samples.append(HKQuantitySample(type: calType, quantity: calQuantity, start: startDate, end: endDate, device: device, metadata: metadata))
            }
        }

        guard !samples.isEmpty else {
            call.resolve(["saved": true, "sampleCount": 0])
            return
        }

        healthStore.save(samples) { success, error in
            if let error = error {
                let desc = error.localizedDescription
                if desc.contains("entitlement") || (error as NSError).code == 4 {
                    call.resolve([
                        "saved": false,
                        "entitlementMissing": true,
                        "sampleCount": samples.count,
                        "message": "HealthKit entitlement missing in provisioning profile. Stored to local fitness matrix."
                    ])
                    return
                }
                call.reject("Failed to batch save samples: \(desc)")
            } else {
                call.resolve([
                    "saved": success,
                    "sampleCount": samples.count
                ])
            }
        }
    }

    @objc func getTodaySteps(_ call: CAPPluginCall) {
        guard HKHealthStore.isHealthDataAvailable(),
              let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount) else {
            call.reject("HealthKit not available")
            return
        }

        let calendar = Calendar.current
        let now = Date()
        let startOfDay = calendar.startOfDay(for: now)
        let predicate = HKQuery.predicateForSamples(withStart: startOfDay, end: now, options: .strictStartDate)

        let query = HKStatisticsQuery(quantityType: stepType, quantitySamplePredicate: predicate, options: .cumulativeSum) { _, result, error in
            if let error = error {
                call.reject("Query failed: \(error.localizedDescription)")
                return
            }
            let sum = result?.sumQuantity()?.doubleValue(for: .count()) ?? 0.0
            call.resolve(["steps": Int(sum)])
        }

        healthStore.execute(query)
    }

    @objc func openShortcutSync(_ call: CAPPluginCall) {
        let name = call.getString("name") ?? "FlashSync"
        let input = call.getString("input") ?? ""
        var allowed = CharacterSet.urlQueryAllowed
        allowed.remove(charactersIn: "+&=")
        let encodedName = name.addingPercentEncoding(withAllowedCharacters: allowed) ?? name
        let encodedInput = input.addingPercentEncoding(withAllowedCharacters: allowed) ?? input
        let urlStr = "shortcuts://run-shortcut?name=\(encodedName)&input=text&text=\(encodedInput)"
        
        guard let url = URL(string: urlStr) else {
            call.reject("Invalid Shortcut URL")
            return
        }
        
        DispatchQueue.main.async {
            UIApplication.shared.open(url, options: [:]) { success in
                call.resolve(["opened": success])
            }
        }
    }

    @objc func openShortcutsApp(_ call: CAPPluginCall) {
        guard let url = URL(string: "shortcuts://") else {
            call.reject("Invalid URL")
            return
        }
        DispatchQueue.main.async {
            UIApplication.shared.open(url, options: [:]) { success in
                call.resolve(["opened": success])
            }
        }
    }
}

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Override point for customization after application launch.
        return true
    }

    func applicationWillResignActive(_ application: UIApplication) {
        // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
        // Use this method to pause ongoing tasks, disable timers, and invalidate graphics rendering callbacks. Games should use this method to pause the game.
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        // Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later.
        // If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
        // Called as part of the transition from the background to the active state; here you can undo many of the changes made on entering the background.
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
        // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
    }

    func applicationWillTerminate(_ application: UIApplication) {
        // Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.
    }

    func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool {
        // Called when the app was launched with a url. Feel free to add additional processing here,
        // but if you want the App API to support tracking app url opens, make sure to keep this call
        return ApplicationDelegateProxy.shared.application(app, open: url, options: options)
    }

    func application(_ application: UIApplication, continue userActivity: NSUserActivity, restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
        // Called when the app was launched with an activity, including Universal Links.
        // Feel free to add additional processing here, but if you want the App API to support
        // tracking app url opens, make sure to keep this call
        return ApplicationDelegateProxy.shared.application(application, continue: userActivity, restorationHandler: restorationHandler)
    }

}
