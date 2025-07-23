#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <fstream>
#include <ctime> 
#include <algorithm>

#include "../game_reader/json.hpp" 
#include "../sdk/public/steam/steam_api.h"

using json = nlohmann::json;
std::string base64_encode(const std::vector<unsigned char>& in) {
    std::string out;
    int val = 0, valb = -6;
    for (unsigned char c : in) {
        val = (val << 8) + c;
        valb += 8;
        while (valb >= 0) {
            out.push_back("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"[(val >> valb) & 0x3F]);
            valb -= 6;
        }
    }
    if (valb > -6) {
        out.push_back("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"[((val << 8) >> (valb + 8)) & 0x3F]);
    }
    while (out.size() % 4) {
        out.push_back('=');
    }
    return out;
}

class CSteamStatsAndAchievements {
private:
    bool m_bStatsValid;
    bool m_bCallbackCompleted;

    CCallResult<CSteamStatsAndAchievements, UserStatsReceived_t> m_UserStatsReceivedCallResult;

public:
    CSteamStatsAndAchievements() : 
        m_bStatsValid(false), 
        m_bCallbackCompleted(false)
    {}

    void RequestStats() {
        m_bStatsValid = false;
        m_bCallbackCompleted = false;
        
        CSteamID steamID = SteamUser()->GetSteamID();
        SteamAPICall_t hSteamAPICall = SteamUserStats()->RequestUserStats(steamID);

        if (hSteamAPICall != 0) {
            m_UserStatsReceivedCallResult.Set(hSteamAPICall, this, &CSteamStatsAndAchievements::OnUserStatsReceived);
        } else {
            std::cerr << "Erro: Falha ao chamar RequestUserStats (retornou 0)." << std::endl;
            m_bCallbackCompleted = true; 
        }
    }

    void OnUserStatsReceived(UserStatsReceived_t *pCallback, bool bIOFailure) {
        if (bIOFailure || pCallback->m_eResult != k_EResultOK) {
            m_bStatsValid = false;
        } else {
            m_bStatsValid = true;
        }
        m_bCallbackCompleted = true; 
    }

    bool IsRequestCompleted() const { return m_bCallbackCompleted; }
    bool AreStatsValid() const { return m_bStatsValid; }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Uso: .\\achievement_fetcher.exe <AppID>" << std::endl;
        return 1;
    }
    std::string appID_str = argv[1];
    std::ofstream appid_file("steam_appid.txt");
    appid_file << appID_str;
    appid_file.close();

    if (!SteamAPI_Init()) {
        std::cerr << "Erro Fatal: SteamAPI_Init() falhou." << std::endl;
        return 1;
    }

    CSteamStatsAndAchievements statsHandler;
    statsHandler.RequestStats();

    const auto startTime = std::chrono::steady_clock::now();
    while (!statsHandler.IsRequestCompleted()) {
        SteamAPI_RunCallbacks();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        auto currentTime = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(currentTime - startTime).count() > 15) {
            std::cerr << "Erro: Timeout." << std::endl;
            SteamAPI_Shutdown();
            return 1;
        }
    }

    if (!statsHandler.AreStatsValid()) {
        std::cerr << "Erro: Nao foi possivel obter as estatisticas para este AppID." << std::endl;
        SteamAPI_Shutdown();
        return 1;
    }

    int numAchievements = SteamUserStats()->GetNumAchievements();
    if (numAchievements == 0) {
        std::cout << "[]" << std::endl; 
        SteamAPI_Shutdown();
        return 0;
    }

    json achievementsJson = json::array();
    for (int i = 0; i < numAchievements; ++i) {
        const char* apiName = SteamUserStats()->GetAchievementName(i);
        if (!apiName) continue;

        bool bAchieved = false;
        RTime32 unlockedTimestamp = 0; 
        
        SteamUserStats()->GetAchievementAndUnlockTime(apiName, &bAchieved, &unlockedTimestamp);
        
        const char* name = SteamUserStats()->GetAchievementDisplayAttribute(apiName, "name");
        const char* desc = SteamUserStats()->GetAchievementDisplayAttribute(apiName, "desc");
        
        json achJson;
        achJson["apiName"] = apiName;
        achJson["isAchieved"] = bAchieved;
        achJson["name"] = name ? name : apiName;
        achJson["description"] = desc ? desc : "";
        achJson["unlockedTimestamp"] = unlockedTimestamp; 
        
        int iconHandle = SteamUserStats()->GetAchievementIcon(apiName);
        if (iconHandle != 0) {
            uint32 width, height;
            if (SteamUtils()->GetImageSize(iconHandle, &width, &height)) {
                std::vector<unsigned char> rgbaData(width * height * 4);
                if (SteamUtils()->GetImageRGBA(iconHandle, rgbaData.data(), width * height * 4)) {
                    achJson["icon_base64"] = base64_encode(rgbaData);
                }
            }
        }
        
        achievementsJson.push_back(achJson);
    }

    std::cout << achievementsJson.dump(4) << std::endl;
    SteamAPI_Shutdown();
    return 0;
}