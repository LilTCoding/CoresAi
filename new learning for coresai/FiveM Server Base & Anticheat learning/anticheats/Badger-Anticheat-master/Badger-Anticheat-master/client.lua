

function Draw3DText(text, radius, pos)
    if Vdist2(GetEntityCoords(PlayerPedId(), false), pos.x,pos.y,pos.z) < (radius) then
        local onScreen, _x, _y = World3dToScreen2d(pos.x,pos.y,pos.z)
        local p = GetEntityCoords(PlayerPedId(), false)
        local distance = GetDistanceBetweenCoords(p.x, p.y, p.z, pos.x,pos.y,pos.z, 1)
        local scale = (1 / distance)
        local fov = (1 / GetGameplayCamFov()) * 75
        local scale = scale * fov
        if onScreen then
            SetTextScale(tonumber(1.0), tonumber(0.35 * (1)))
            SetTextFont(0)
            SetTextProportional(true)
            SetTextColour(255, 255, 255, 255)
            SetTextOutline()
            SetTextEntry("STRING")
            SetTextCentre(true)
            AddTextComponentString(text)
            DrawText(_x,_y)
        end
    end
end
function NetworkDelete(entity)
    Citizen.CreateThread(function()
        if DoesEntityExist(entity) and not (IsEntityAPed(entity) and IsPedAPlayer(entity)) then
            NetworkRequestControlOfEntity(entity)
            local timeout = 5
            while timeout > 0 and not NetworkHasControlOfEntity(entity) do
                Citizen.Wait(1)
                timeout = timeout - 1
            end
            DetachEntity(entity, 0, false)
            SetEntityCollision(entity, false, false)
            SetEntityAlpha(entity, 0.0, true)
            SetEntityAsMissionEntity(entity, true, true)
            SetEntityAsNoLongerNeeded(entity)
            DeleteEntity(entity)
        end
    end)
end
-- Prevent most injection:
if Config.Components.AntiCommands then 
    Citizen.CreateThread(function()
        Citizen.Wait(120000);
        while true do
            Citizen.Wait(500);
            local blacklistedCommands = Config.BlacklistedCommands or {}
            local registeredCommands = GetRegisteredCommands()

            for _, command in ipairs(registeredCommands) do
                for _, blacklistedCommand in pairs(blacklistedCommands) do
                    if (string.lower(command.name) == string.lower(blacklistedCommand) or
                        string.lower(command.name) == string.lower('+' .. blacklistedCommand) or
                        string.lower(command.name) == string.lower('_' .. blacklistedCommand) or
                        string.lower(command.name) == string.lower('-' .. blacklistedCommand) or
                        string.lower(command.name) == string.lower('/' .. blacklistedCommand)) then
                        TriggerServerEvent("Anticheat:Modder", "CONFIRMED HACKER [Lua Injection]", 
                            "Why you injecting Lua code? Stoopid ass hoe");
                    end
                end
            end
        end
    end)
end 
RegisterNetEvent("anticheat:EntityWipe")
AddEventHandler("anticheat:EntityWipe", function(id)
    Citizen.CreateThread(function() 
        for k,v in pairs(GetAllEnumerators()) do 
            local enum = v
            for entity in enum() do 
                local owner = NetworkGetEntityOwner(entity)
                local playerID = GetPlayerServerId(owner)
                if (owner ~= -1 and (id == playerID or id == -1)) then
                    NetworkDelete(entity)
                end
            end
        end
    end)
end)

if Config.Components.AntiESX then 
    RegisterNetEvent('esx:getSharedObject')
    AddEventHandler('esx:getSharedObject', function()
        TriggerServerEvent("Anticheat:ModderESX", "CONFIRMED HACKER [Getting ESX object via client code]", 
                            "Why you injecting Lua code? Stoopid ass hoe");
    end)
end

if Config.Components.AntiKeys then 
    -- Prevent keys from being Released 
    Citizen.CreateThread(function()
        while true do 
            Wait(0);
            local blacklistedKeys = Config.BlacklistedKeys;
            for i = 1, #blacklistedKeys do 
                local keyCombo = blacklistedKeys[i][1];
                local keyStr = blacklistedKeys[i][2];
                if #keyCombo == 1 then 
                    local key1 = keyCombo[1];
                    if IsDisabledControlJustReleased(0, key1) then 
                        -- They are using a blacklisted key 
                        if Config.KickForKeys then 
                            TriggerServerEvent("Anticheat:ModderNoKick", "HACKER (Probably) [Key Press: `" .. keyStr ..
                                "`]", "Why you opening a mod menu? Stoopid ass hoe", true);
                        else
                            TriggerServerEvent("Anticheat:ModderNoKick", "HACKER (Probably) [Key Press: `" .. keyStr ..
                                "`]", "Why you opening a mod menu? Stoopid ass hoe", false);
                        end
                    end
                elseif #keyCombo == 2 then 
                    local key1 = keyCombo[1];
                    local key2 = keyCombo[2];
                    if IsDisabledControlPressed(0, key1) and IsDisabledControlPressed(0, key2) then 
                        -- They are using blacklisted keys 
                        if Config.KickForKeys then 
                            TriggerServerEvent("Anticheat:ModderNoKick", "HACKER (Probably) [Key Press: `" .. keyStr ..
                                "`]", "Why you opening a mod menu? Stoopid ass hoe", true);
                        else
                            TriggerServerEvent("Anticheat:ModderNoKick", "HACKER (Probably) [Key Press: `" .. keyStr ..
                                "`]", "Why you opening a mod menu? Stoopid ass hoe", false);
                        end
                        Wait(20000); -- Wait 20 seconds 
                    end
                elseif #keyCombo == 3 then 
                    local key1 = keyCombo[1];
                    local key2 = keyCombo[2];
                    local key3 = keyCombo[3];
                    if IsDisabledControlPressed(0, key1) and IsDisabledControlPressed(0, key2) and 
                    IsDisabledControlPressed(0, key3) then 
                        -- They are using blacklisted keys 
                        if Config.KickForKeys then 
                            TriggerServerEvent("Anticheat:ModderNoKick", "HACKER (Probably) [Key Press: `" .. keyStr ..
                                "`]", "Why you opening a mod menu? Stoopid ass hoe", true);
                        else
                            TriggerServerEvent("Anticheat:ModderNoKick", "HACKER (Probably) [Key Press: `" .. keyStr ..
                                "`]", "Why you opening a mod menu? Stoopid ass hoe", false);
                        end
                    end
                    Wait(20000); -- Wait 20 seconds 
                elseif #keyCombo == 4 then 
                    local key1 = keyCombo[1];
                    local key2 = keyCombo[2];
                    local key3 = keyCombo[3];
                    local key4 = keyCombo[4];
                    if IsDisabledControlPressed(0, key1) and IsDisabledControlPressed(0, key2) and 
                    IsDisabledControlPressed(0, key3) and IsDisabledControlPressed(0, key4) then 
                        -- They are using blacklisted keys 
                        if Config.KickForKeys then 
                            TriggerServerEvent("Anticheat:ModderNoKick", "HACKER (Probably) [Key Press: `" .. keyStr ..
                                "`]", "Why you opening a mod menu? Stoopid ass hoe", true);
                        else
                            TriggerServerEvent("Anticheat:ModderNoKick", "HACKER (Probably) [Key Press: `" .. keyStr ..
                                "`]", "Why you opening a mod menu? Stoopid ass hoe", false);
                        end
                    end
                    Wait(20000); -- Wait 20 seconds 
                end
            end
        end
    end)
end
-- prevent infinite ammo, godmode, invisibility and ped speed hacks 
-- Props to Anticheese Anticheat for this: [https://github.com/Bluethefurry]
if Config.Components.AntiCheat then
    Citizen.CreateThread(function()
        while true do
            Citizen.Wait(1)
            SetPedInfiniteAmmoClip(PlayerPedId(), false)
            SetEntityInvincible(PlayerPedId(), false)
            SetEntityCanBeDamaged(PlayerPedId(), true)
            ResetEntityAlpha(PlayerPedId())
            local fallin = IsPedFalling(PlayerPedId())
            local ragg = IsPedRagdoll(PlayerPedId())
            local parac = GetPedParachuteState(PlayerPedId())
            if parac >= 0 or ragg or fallin then
                SetEntityMaxSpeed(PlayerPedId(), 80.0)
            else
                SetEntityMaxSpeed(PlayerPedId(), 7.1)
            end
        end
    end)
end
-- End props 
--[[]]--
-- Props to Anticheese Anticheat for this: [https://github.com/Bluethefurry]
if Config.Components.AntiSpeedhack then
    Citizen.CreateThread(function()
        Citizen.Wait(30000)
        while true do
            Citizen.Wait(0)
            local ped = PlayerPedId()
            local posx,posy,posz = table.unpack(GetEntityCoords(ped,true))
            local still = IsPedStill(ped)
            local vel = GetEntitySpeed(ped)
            local ped = PlayerPedId()
            local veh = IsPedInAnyVehicle(ped, true)
            local speed = GetEntitySpeed(ped)
            local para = GetPedParachuteState(ped)
            local flyveh = IsPedInFlyingVehicle(ped)
            local rag = IsPedRagdoll(ped)
            local fall = IsPedFalling(ped)
            local parafall = IsPedInParachuteFreeFall(ped)
            SetEntityVisible(PlayerPedId(), true) -- make sure player is visible
            Wait(3000) -- wait 3 seconds and check again

            local more = speed - 9.0 -- avarage running speed is 7.06 so just incase someone runs a bit faster it wont trigger

            local rounds = tonumber(string.format("%.2f", speed))
            local roundm = tonumber(string.format("%.2f", more))


            if not IsEntityVisible(PlayerPedId()) then
                SetEntityHealth(PlayerPedId(), -100) -- if player is invisible kill him!
            end

            newx,newy,newz = table.unpack(GetEntityCoords(ped,true))
            newPed = PlayerPedId() -- make sure the peds are still the same, otherwise the player probably respawned
            if GetDistanceBetweenCoords(posx,posy,posz, newx,newy,newz) > 200 and still == IsPedStill(ped) and vel == GetEntitySpeed(ped) and ped == newPed then
                TriggerServerEvent("Anticheat:NoClip", GetDistanceBetweenCoords(posx,posy,posz, newx,newy,newz))
            end
        end
    end)
end
-- End props 
--[[]]--


Citizen.CreateThread(function()
    while true do
        Wait(3000);
        local ped = NetworkIsInSpectatorMode()
        if ped == 1 then
            TriggerServerEvent("Anticheat:SpectateTrigger", "Why are you stalking someone? Stoopid ass hoe");
        end
    end
end)