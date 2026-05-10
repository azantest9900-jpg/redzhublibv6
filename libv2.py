--[[
    RedzLibrary - Clean Rewrite
    A full-featured Roblox UI Library
    Version: 1.0.0
--]]

-- ============================================================
--  SERVICES
-- ============================================================

local Players           = game:GetService("Players")
local TweenService      = game:GetService("TweenService")
local UserInputService  = game:GetService("UserInputService")
local RunService        = game:GetService("RunService")
local HttpService       = game:GetService("HttpService")
local MarketplaceService= game:GetService("MarketplaceService")

local LocalPlayer = Players.LocalPlayer
local Mouse       = LocalPlayer:GetMouse()
local Camera      = workspace.CurrentCamera

-- ============================================================
--  EXECUTOR COMPATIBILITY
-- ============================================================

local cloneref    = cloneref    or function(...) return ... end
local gethui      = gethui      or function() return game:GetService("CoreGui") end
local writefile   = writefile   or nil
local readfile    = readfile    or nil
local makefolder  = makefolder  or nil
local deletefile  = deletefile  or nil
local isfile      = isfile      or nil
local isfolder    = isfolder    or nil
local setclipboard= setclipboard or nil

-- ============================================================
--  THEME DEFINITIONS
-- ============================================================

local Themes = {
    Darker = {
        Name = "Darker",

        Background = ColorSequence.new({
            ColorSequenceKeypoint.new(0.00, Color3.fromRGB(25, 25, 25)),
            ColorSequenceKeypoint.new(0.50, Color3.fromRGB(32, 32, 32)),
            ColorSequenceKeypoint.new(1.00, Color3.fromRGB(25, 25, 25)),
        }),

        Primary     = Color3.fromRGB(88, 101, 242),
        OnPrimary   = Color3.fromRGB(61, 67, 135),
        ScrollBar   = Color3.fromRGB(1, 76, 105),
        Stroke      = Color3.fromRGB(45, 45, 45),
        Error       = Color3.fromRGB(255, 102, 102),
        Icons       = Color3.fromRGB(232, 233, 235),
        JoinButton  = Color3.fromRGB(37, 128, 69),
        Link        = Color3.fromRGB(40, 150, 255),

        BackgroundTransparency = 0.03,

        Dialog = {
            Background = Color3.fromRGB(28, 28, 28),
        },

        Buttons = {
            Holding = Color3.fromRGB(34, 34, 34),
            Default = Color3.fromRGB(28, 28, 30),
        },

        Border = {
            Holding = Color3.fromRGB(60, 60, 60),
            Default = Color3.fromRGB(38, 38, 38),
        },

        Text = {
            Default = Color3.fromRGB(255, 255, 255),
            Dark    = Color3.fromRGB(200, 200, 200),
            Darker  = Color3.fromRGB(175, 175, 175),
        },

        Slider = {
            SliderBar    = Color3.fromRGB(1, 76, 105),
            SliderNumber = Color3.fromRGB(232, 233, 235),
        },

        Dropdown = {
            Holder = Color3.fromRGB(30, 30, 30),
        },

        Icons = {
            Error    = "rbxassetid://10709752996",
            Button   = "rbxassetid://10709791437",
            Close    = "rbxassetid://10747384394",
            TextBox  = "rbxassetid://15637081879",
            Search   = "rbxassetid://10734943674",
            Keybind  = "rbxassetid://10734982144",
            Dropdown = {
                Open  = "rbxassetid://10709791523",
                Close = "rbxassetid://10709790948",
            },
        },

        Font = {
            Normal    = Enum.Font.BuilderSans,
            Medium    = Enum.Font.BuilderSansMedium,
            Bold      = Enum.Font.BuilderSansBold,
            ExtraBold = Enum.Font.BuilderSansExtraBold,
            SliderValue = Enum.Font.FredokaOne,
        },
    }
}

-- ============================================================
--  LIBRARY TABLE
-- ============================================================

local Library = {
    Version  = "1.0.0",
    Themes   = Themes,
    Options  = {},   -- flag storage (key = flagName, value = current value)
    Icons    = {},   -- custom icon name -> assetId map
    Connections = {},

    CurrentTheme = nil,
    Loaded = false,

    -- defaults
    Default = {
        Theme   = "Darker",
        UISize  = UDim2.fromOffset(550, 380),
        TabSize = 160,
    },
}

-- ============================================================
--  UTILITY FUNCTIONS
-- ============================================================

-- Tween shorthand
local function Tween(instance, property, goal, duration, style, direction)
    style     = style     or Enum.EasingStyle.Quint
    direction = direction or Enum.EasingDirection.Out
    local info = TweenInfo.new(duration, style, direction)
    return TweenService:Create(instance, info, { [property] = goal })
end

-- Connect and track a connection
local function Connect(signal, callback)
    local conn = signal:Connect(callback)
    table.insert(Library.Connections, conn)
    return conn
end

-- Safely write a file, creating folders as needed
local function SafeWrite(path, content)
    if not writefile then return end
    if makefolder then
        local parts = path:split("/")
        parts[#parts] = nil
        local folder = table.concat(parts, "/")
        if folder ~= "" and (not isfolder or not isfolder(folder)) then
            makefolder(folder)
        end
    end
    writefile(path, content)
end

-- Strip special characters for search matching
local function Normalize(str)
    return str:lower():gsub("[%p%s]", "")
end

-- Format a number with commas
local function FormatNumber(n)
    local s = tostring(math.floor(n))
    local result = ""
    local count  = 0
    for i = #s, 1, -1 do
        result = s:sub(i, i) .. result
        count += 1
        if count % 3 == 0 and i > 1 then
            result = "," .. result
        end
    end
    return result
end

-- Format seconds into readable time
local function FormatTime(seconds)
    local h = math.floor(seconds / 3600)
    local m = math.floor((seconds % 3600) / 60)
    local s = math.floor(seconds % 60)
    if h > 0 then return ("%dh %dm %ds"):format(h, m, s) end
    if m > 0 then return ("%dm %ds"):format(m, s) end
    return tostring(s)
end

-- Check if a string is a Roblox asset ID URL
local function IsAssetId(str)
    return type(str) == "string" and str:sub(1, 13) == "rbxassetid://"
end

-- Scale a value based on viewport height
local function ScaleToViewport(value)
    return (Camera.ViewportSize.Y / 450) * value
end

-- Get a theme value by dot-path, e.g. "Text.Default"
local function GetThemeValue(theme, path)
    local current = theme
    for key in path:gmatch("[^%.]+") do
        current = current[key]
        if current == nil then return nil end
    end
    return current
end

-- Get icon by name from library icon map
function Library:GetIconByName(name)
    if name == nil then return nil end
    if IsAssetId(name) or #name == 0 then return name end

    local normalized = Normalize(name)
    if self.Icons[normalized] then
        return "rbxassetid://" .. self.Icons[normalized]
    end
    for key, id in self.Icons do
        if key:find(normalized, 1, true) then
            return "rbxassetid://" .. id
        end
    end
    return nil
end

-- ============================================================
--  INSTANCE BUILDER
-- ============================================================

-- Builds a Roblox instance with a property table.
-- Special keys: Parent, Children, Name
local function New(className, properties)
    local instance = Instance.new(className)
    local children = properties and properties.Children
    local parent   = properties and properties.Parent

    if properties then
        for key, value in properties do
            if key ~= "Parent" and key ~= "Children" then
                instance[key] = value
            end
        end
    end

    if children then
        for _, child in children do
            child.Parent = instance
        end
    end

    if parent then
        instance.Parent = parent
    end

    return instance
end

-- ============================================================
--  DRAGGING
-- ============================================================

local DragTarget = nil  -- which frame is currently being dragged
local IsDragging = false

local function MakeDraggable(frame, scaleRef, smoothing, constraintFn)
    smoothing = smoothing or 0.28

    Connect(frame.InputBegan, function(input)
        if IsDragging then return end
        local validTypes = {
            [Enum.UserInputType.MouseButton1] = true,
            [Enum.UserInputType.Touch]        = true,
        }
        if not validTypes[input.UserInputType] then return end

        local startInputPos = input.Position
        local startFramePos = frame.Position
        local lastTime      = tick()
        DragTarget = frame
        IsDragging = true

        local function stopDrag()
            IsDragging = false
            DragTarget = nil
        end

        Connect(input.Changed, function()
            if input.UserInputState == Enum.UserInputState.End then
                stopDrag()
            end
        end)

        Connect(UserInputService.InputChanged, function(moved)
            if DragTarget ~= frame then return end
            local moveTypes = {
                [Enum.UserInputType.MouseMovement] = true,
                [Enum.UserInputType.Touch]         = true,
            }
            if not moveTypes[moved.UserInputType] then return end

            local delta  = moved.Position - startInputPos
            local scale  = scaleRef and scaleRef.Scale or 1
            local newPos

            if constraintFn then
                newPos = constraintFn(
                    startFramePos.X.Scale,
                    startFramePos.X.Offset + delta.X / scale,
                    startFramePos.Y.Scale,
                    startFramePos.Y.Offset + delta.Y / scale
                )
            else
                newPos = UDim2.new(
                    startFramePos.X.Scale,
                    startFramePos.X.Offset + delta.X / scale,
                    startFramePos.Y.Scale,
                    startFramePos.Y.Offset + delta.Y / scale
                )
            end

            lastTime = tick()
            frame.Position = frame.Position:Lerp(newPos, smoothing)
        end)
    end)
end

-- ============================================================
--  ELEMENT BASE (metatable shared by all elements)
-- ============================================================

local ElementBase = {}
ElementBase.__index = ElementBase

function ElementBase:SetTitle(text)
    assert(type(text) == "string", "SetTitle: string expected")
    if self.TitleLabel then
        self.TitleLabel.Text = text
        self.Title = text
    end
    return self
end

function ElementBase:SetDescription(text)
    assert(text == nil or type(text) == "string", "SetDescription: string or nil expected")
    if self.DescLabel then
        self.DescLabel.Text = text or ""
        self.Description = text
    end
    return self
end

function ElementBase:SetVisible(visible)
    assert(type(visible) == "boolean", "SetVisible: boolean expected")
    if self.VisibleFrame then
        self.VisibleFrame.Visible = visible
    end
end

function ElementBase:Destroy()
    if self.RootFrame then
        self.RootFrame:Destroy()
    end
    setmetatable(self, nil)
    self.Destroyed = true
end

function ElementBase:AddCallback(fn)
    assert(type(fn) == "function", "AddCallback: function expected")
    if self.Callbacks then
        table.insert(self.Callbacks, fn)
    end
    return self
end

ElementBase.NewCallback  = ElementBase.AddCallback
ElementBase.SetContent   = ElementBase.SetDescription
ElementBase.SetDesc      = ElementBase.SetDescription

-- Fire all callbacks
local function FireCallbacks(callbacks, ...)
    if not callbacks then return end
    for _, fn in callbacks do
        task.spawn(fn, ...)
    end
end

-- ============================================================
--  ELEMENT ROW BUILDER
-- Builds the standard option row used by most elements.
-- Returns: rootButton, titleLabel, descLabel
-- ============================================================

local function BuildOptionRow(container, theme, titleText, descText, rightWidth)
    rightWidth = rightWidth or UDim2.new(0, 0, 0, 0)

    local titleSize = UDim2.new(1, -(rightWidth.X.Offset + 20), 0, 0)

    local titleLabel = New("TextLabel", {
        Name                  = "Title",
        BackgroundTransparency = 1,
        TextXAlignment        = Enum.TextXAlignment.Left,
        TextTruncate          = Enum.TextTruncate.AtEnd,
        AutomaticSize         = Enum.AutomaticSize.Y,
        Size                  = titleSize,
        Position              = UDim2.fromScale(0, 0.5),
        AnchorPoint           = Vector2.new(0, 0.5),
        TextSize              = 11,
        Text                  = titleText,
        Font                  = theme.Font.Medium,
        TextColor3            = theme.Text.Default,
    })

    local descLabel = New("TextLabel", {
        Name                  = "Description",
        BackgroundTransparency = 1,
        TextXAlignment        = Enum.TextXAlignment.Left,
        AutomaticSize         = Enum.AutomaticSize.Y,
        Size                  = UDim2.new(1, -20, 0, 0),
        Position              = UDim2.new(0, 12, 0, 15),
        TextWrapped           = true,
        TextSize              = 8,
        RichText              = true,
        Text                  = descText or "",
        Font                  = theme.Font.Normal,
        TextColor3            = theme.Text.Dark,
    })

    local holder = New("Frame", {
        Name              = "Holder",
        AutomaticSize     = Enum.AutomaticSize.Y,
        BackgroundTransparency = 1,
        Size              = UDim2.fromScale(1, 1),
        Children = {
            New("UIListLayout", {
                SortOrder          = Enum.SortOrder.LayoutOrder,
                VerticalAlignment  = Enum.VerticalAlignment.Center,
                Padding            = UDim.new(0, 2),
            }),
            New("UIPadding", {
                PaddingTop    = UDim.new(0, 5),
                PaddingBottom = UDim.new(0, 5),
            }),
            titleLabel,
            descLabel,
        }
    })

    local rootButton = New("TextButton", {
        Name              = "OptionButton",
        AutomaticSize     = Enum.AutomaticSize.Y,
        Size              = UDim2.new(1, 0, 0, 25),
        AutoButtonColor   = false,
        Text              = "",
        BackgroundColor3  = theme.Buttons.Default,
        Parent            = container,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0, 6) }),
            holder,
        }
    })

    -- Hover effect
    Connect(rootButton.MouseEnter, function()
        Tween(rootButton, "BackgroundColor3", theme.Buttons.Holding, 0.2):Play()
    end)
    Connect(rootButton.MouseLeave, function()
        Tween(rootButton, "BackgroundColor3", theme.Buttons.Default, 0.2):Play()
    end)

    -- Show/hide description
    Connect(descLabel:GetPropertyChangedSignal("Text"), function()
        local hasDesc = #descLabel.Text > 0
        descLabel.Visible = hasDesc
        holder.Position   = UDim2.fromScale(0, hasDesc and 0 or 0.5)
        holder.AnchorPoint= Vector2.new(0, hasDesc and 0 or 0.5)
    end)

    -- Trigger initial visibility
    descLabel.Visible = #descLabel.Text > 0

    return rootButton, titleLabel, descLabel
end

-- ============================================================
--  TAB CONTENT CONTAINER
-- ============================================================

local function BuildTabContainer(containerHolder)
    local scrollFrame = New("ScrollingFrame", {
        Name                   = "Container",
        Size                   = UDim2.fromScale(1, 1),
        BackgroundTransparency = 1,
        ScrollBarThickness     = 1.5,
        ScrollBarImageTransparency = 0.2,
        AutomaticCanvasSize    = Enum.AutomaticSize.Y,
        ScrollingDirection     = Enum.ScrollingDirection.Y,
        BorderSizePixel        = 0,
        CanvasSize             = UDim2.new(),
        Parent                 = containerHolder,
        Children = {
            New("UIPadding", {
                PaddingLeft   = UDim.new(0, 10),
                PaddingRight  = UDim.new(0, 10),
                PaddingTop    = UDim.new(0, 10),
                PaddingBottom = UDim.new(0, 10),
            }),
            New("UIListLayout", {
                Padding = UDim.new(0, 5),
            }),
        }
    })
    return scrollFrame
end

-- ============================================================
--  TAB CLASS
-- ============================================================

local Tab = {}
Tab.__index = Tab

function Tab:Select()
    if self._window._selectedTab == self then return end

    if self._window._selectedTab then
        self._window._selectedTab:_deselect()
    end

    self._window._selectedTab = self
    self._contentFrame.Parent = self._window._containerHolder
    self._contentFrame.Size   = UDim2.new(1, 0, 1, 0)
    self.Selected = true

    Tween(self._indicator, "Size",               UDim2.fromOffset(4, 13), 0.3):Play()
    Tween(self._indicator, "BackgroundTransparency", 0, 0.3):Play()
    Tween(self._tabButton.Title, "TextTransparency", 0, 0.3):Play()
end

function Tab:_deselect()
    self.Selected = false
    self._contentFrame.Parent = nil

    Tween(self._indicator, "Size",               UDim2.fromOffset(4, 4), 0.3):Play()
    Tween(self._indicator, "BackgroundTransparency", 1, 0.3):Play()
    Tween(self._tabButton.Title, "TextTransparency", 0.3, 0.3):Play()
end

function Tab:SetVisible(visible)
    self._tabButton.Visible      = visible
    self._contentFrame.Visible   = visible
end

function Tab:Destroy()
    local idx = table.find(self._window._tabs, self)
    if idx then table.remove(self._window._tabs, idx) end
    self._tabButton:Destroy()
    self._contentFrame:Destroy()
    setmetatable(self, nil)
end

-- ---- Element adders ----

function Tab:AddSection(title)
    title = title or ""
    local theme = Library.CurrentTheme

    local frame = New("Frame", {
        Name              = "Section",
        Size              = UDim2.new(1, 0, 0, 20),
        BackgroundTransparency = 1,
        Parent            = self._container,
        Children = {
            New("TextLabel", {
                TextXAlignment = Enum.TextXAlignment.Left,
                TextTruncate   = Enum.TextTruncate.AtEnd,
                Size           = UDim2.new(1, -25, 1, 0),
                Position       = UDim2.new(0, 5, 0, 0),
                BackgroundTransparency = 1,
                TextSize       = 17,
                Text           = title,
                Font           = theme.Font.Bold,
                TextColor3     = theme.Text.Default,
            })
        }
    })

    local element = setmetatable({
        Title        = title,
        Kind         = "Section",
        RootFrame    = frame,
        VisibleFrame = frame,
        Parent       = self,
    }, ElementBase)

    return element
end

function Tab:AddToggle(config)
    assert(type(config) == "table", "AddToggle: table expected")

    local title    = config[1] or config.Title or config.Name or "Toggle"
    local default  = config[2] or config.Default or false
    local callback = config[3] or config.Callback
    local flag     = config[4] or config.Flag

    assert(type(title)   == "string",  "AddToggle.Title: string expected")
    assert(type(default) == "boolean", "AddToggle.Default: boolean expected")

    local theme     = Library.CurrentTheme
    local callbacks = callback and { callback } or {}

    -- Restore from flags
    if flag and type(Library.Options[flag]) == "number" then
        default = Library.Options[flag] == 0
    end

    local rootButton, titleLabel, descLabel = BuildOptionRow(
        self._container, theme,
        title, config.Description or config.Desc or "",
        UDim2.new(0, 38, 0, 0)
    )

    -- Toggle track
    local track = New("Frame", {
        Size        = UDim2.new(0, 35, 0, 18),
        Position    = UDim2.new(1, -10, 0.5, 0),
        AnchorPoint = Vector2.new(1, 0.5),
        Parent      = rootButton,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0.5, 0) }),
        }
    })

    local thumb = New("Frame", {
        Size        = UDim2.new(0, 12, 0, 12),
        Position    = UDim2.new(0, 0, 0.5, 0),
        AnchorPoint = Vector2.new(0, 0.5),
        Parent      = track,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0.5, 0) }),
        }
    })

    local element = setmetatable({
        Title        = title,
        Description  = config.Description or "",
        Kind         = "Toggle",
        Value        = false,
        Callbacks    = callbacks,
        RootFrame    = rootButton,
        VisibleFrame = rootButton,
        TitleLabel   = titleLabel,
        DescLabel    = descLabel,
        Parent       = self,
    }, ElementBase)

    local debounce = 0
    local ANIM_TIME = 0.2

    local function applyValue(value, animate)
        element.Value = value
        if flag then Library.Options[flag] = value and 0 or 1 end

        local thumbPos   = UDim2.new(value and 1 or 0, 0, 0.5, 0)
        local thumbAnch  = Vector2.new(value and 1 or 0, 0.5)
        local trackColor = value and theme.Primary or theme.Stroke
        local thumbColor = value and theme.Primary or theme.OnPrimary

        if animate then
            Tween(thumb,  "Position",       thumbPos,   ANIM_TIME):Play()
            Tween(thumb,  "AnchorPoint",    thumbAnch,  ANIM_TIME):Play()
            Tween(thumb,  "BackgroundColor3", thumbColor, ANIM_TIME):Play()
            Tween(track,  "BackgroundColor3", trackColor, ANIM_TIME):Play()
        else
            thumb.Position        = thumbPos
            thumb.AnchorPoint     = thumbAnch
            thumb.BackgroundColor3 = thumbColor
            track.BackgroundColor3 = trackColor
        end

        FireCallbacks(callbacks, value)
    end

    function element:SetValue(value)
        assert(type(value) == "boolean", "Toggle.SetValue: boolean expected")
        if self.Value ~= value then
            applyValue(value, true)
        end
    end

    element.Set = element.SetValue

    -- Initialize
    applyValue(default, false)

    Connect(rootButton.Activated, function()
        if (tick() - debounce) < ANIM_TIME then return end
        debounce = tick()
        element:SetValue(not element.Value)
    end)

    return element
end

function Tab:AddButton(config)
    assert(type(config) == "table", "AddButton: table expected")

    local title    = config[1] or config.Title or config.Name or "Button"
    local callback = config[2] or config.Callback
    local cooldown = config.Debounce or config.Cooldown

    local theme     = Library.CurrentTheme
    local callbacks = callback and { callback } or {}

    local rootButton, titleLabel, descLabel = BuildOptionRow(
        self._container, theme,
        title, config.Description or config.Desc or "",
        UDim2.new(0, 20, 0, 0)
    )

    -- Arrow icon
    New("ImageLabel", {
        Size        = UDim2.new(0, 14, 0, 14),
        Position    = UDim2.new(1, -10, 0.5, 0),
        AnchorPoint = Vector2.new(1, 0.5),
        BackgroundTransparency = 1,
        Image       = theme.Icons.Button,
        ImageColor3 = theme.Icons,
        Parent      = rootButton,
    })

    local lastClick = 0

    Connect(rootButton.Activated, function()
        if cooldown and (tick() - lastClick) < cooldown then return end
        lastClick = tick()
        FireCallbacks(callbacks)
    end)

    local element = setmetatable({
        Title        = title,
        Description  = config.Description or "",
        Kind         = "Button",
        Callbacks    = callbacks,
        RootFrame    = rootButton,
        VisibleFrame = rootButton,
        TitleLabel   = titleLabel,
        DescLabel    = descLabel,
        Parent       = self,
    }, ElementBase)

    return element
end

function Tab:AddSlider(config)
    assert(type(config) == "table", "AddSlider: table expected")

    local title     = config[1] or config.Title or config.Name or "Slider"
    local min       = config[2] or config.Min   or 0
    local max       = config[3] or config.Max   or 100
    local increment = config[4] or config.Increment or 1
    local default   = config[5] or config.Default  or min
    local callback  = config[6] or config.Callback
    local flag      = config[7] or config.Flag

    assert(type(min) == "number", "AddSlider.Min: number expected")
    assert(type(max) == "number", "AddSlider.Max: number expected")

    local theme     = Library.CurrentTheme
    local callbacks = callback and { callback } or {}

    if flag and type(Library.Options[flag]) == "number" then
        default = Library.Options[flag]
    end

    local rootButton, titleLabel, descLabel = BuildOptionRow(
        self._container, theme,
        title, config.Description or config.Desc or "",
        UDim2.new(0.45, 0, 0, 0)
    )

    -- Right side slider area
    local sliderArea = New("TextButton", {
        Size        = UDim2.new(0.45, 0, 1, 0),
        Position    = UDim2.new(1, 0, 0, 0),
        AnchorPoint = Vector2.new(1, 0),
        AutoButtonColor = false,
        BackgroundTransparency = 1,
        Text        = "",
        Parent      = rootButton,
    })

    local track = New("Frame", {
        Size        = UDim2.new(1, -20, 0, 6),
        Position    = UDim2.fromScale(0.5, 0.5),
        AnchorPoint = Vector2.new(0.5, 0.5),
        BackgroundColor3 = theme.Stroke,
        Parent      = sliderArea,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0.5, 0) }),
        }
    })

    local fill = New("Frame", {
        Size        = UDim2.fromScale(0, 1),
        BackgroundColor3 = theme.Primary,
        Parent      = track,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0.5, 0) }),
        }
    })

    local thumb = New("Frame", {
        Size        = UDim2.new(0, 6, 0, 12),
        Position    = UDim2.fromScale(0, 0.5),
        AnchorPoint = Vector2.new(0.5, 0.5),
        BackgroundColor3 = Color3.fromRGB(220, 220, 220),
        BackgroundTransparency = 0.2,
        Parent      = track,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0, 6) }),
        }
    })

    local valueLabel = New("TextLabel", {
        Size        = UDim2.new(0, 50, 0, 14),
        AnchorPoint = Vector2.new(1, 0.5),
        Position    = UDim2.new(0, -1, 0.5, 0),
        BackgroundTransparency = 1,
        TextSize    = 12,
        TextXAlignment = Enum.TextXAlignment.Right,
        Font        = theme.Font.SliderValue,
        TextColor3  = theme.Text.Default,
        Parent      = sliderArea,
    })

    local element = setmetatable({
        Title        = title,
        Description  = config.Description or "",
        Kind         = "Slider",
        Value        = default,
        Min          = min,
        Max          = max,
        Increment    = increment,
        Callbacks    = callbacks,
        RootFrame    = rootButton,
        VisibleFrame = rootButton,
        TitleLabel   = titleLabel,
        DescLabel    = descLabel,
        Parent       = self,
    }, ElementBase)

    local function toPercent(value)
        return (value - min) / (max - min)
    end

    local function snapValue(raw)
        return math.clamp(math.round(raw / increment) * increment, min, max)
    end

    local function applyValue(value, animate)
        value = snapValue(value)
        if value == element.Value and animate then return end
        element.Value = value
        if flag then Library.Options[flag] = value end

        local pct = toPercent(value)
        valueLabel.Text = tostring(math.floor(value * 1000) / 1000)

        if animate and self.Selected then
            Tween(thumb, "Position", UDim2.fromScale(pct, 0.5), 0.3):Play()
            Tween(fill,  "Size",     UDim2.fromScale(pct, 1),   0.3):Play()
        else
            thumb.Position = UDim2.fromScale(pct, 0.5)
            fill.Size      = UDim2.fromScale(pct, 1)
        end

        task.defer(FireCallbacks, callbacks, value)
    end

    function element:SetValue(value)
        assert(type(value) == "number", "Slider.SetValue: number expected")
        applyValue(value, true)
    end

    element.Set = element.SetValue

    -- Initialize
    applyValue(default, false)

    -- Drag interaction
    Connect(sliderArea.MouseButton1Down, function()
        if IsDragging then return end
        IsDragging = true
        Tween(thumb, "BackgroundTransparency", 0, 0.3):Play()
        self._container.ScrollingEnabled = false

        while UserInputService:IsMouseButtonPressed(Enum.UserInputType.MouseButton1) do
            local absPos  = track.AbsolutePosition
            local absSize = track.AbsoluteSize
            local pct     = math.clamp((Mouse.X - absPos.X) / absSize.X, 0, 1)
            applyValue(min + pct * (max - min), false)
            task.wait()
        end

        IsDragging = false
        Tween(thumb, "BackgroundTransparency", 0.2, 0.3):Play()
        self._container.ScrollingEnabled = true
    end)

    return element
end

function Tab:AddTextBox(config)
    assert(type(config) == "table", "AddTextBox: table expected")

    local title       = config[1] or config.Title or config.Name or "TextBox"
    local default     = config[2] or config.Default
    local callback    = config[3] or config.Callback
    local flag        = config[4] or config.Flag
    local placeholder = config.Placeholder or config.PlaceholderText or "Input"
    local clearOnFocus= config.ClearOnFocus or config.ClearTextOnFocus

    local theme     = Library.CurrentTheme
    local callbacks = callback and { callback } or {}

    if flag and type(Library.Options[flag]) == "string" then
        default = Library.Options[flag]
    end

    local rootButton, titleLabel, descLabel = BuildOptionRow(
        self._container, theme,
        title, config.Description or config.Desc or "",
        UDim2.new(0, 150, 0, 0)
    )

    local boxFrame = New("Frame", {
        Size        = UDim2.new(0, 150, 0, 18),
        Position    = UDim2.new(1, -10, 0.5, 0),
        AnchorPoint = Vector2.new(1, 0.5),
        BackgroundColor3 = theme.Stroke,
        Parent      = rootButton,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0, 4) }),
        }
    })

    local textBox = New("TextBox", {
        Size        = UDim2.new(0.85, 0, 0.85, 0),
        AnchorPoint = Vector2.new(0.5, 0.5),
        Position    = UDim2.fromScale(0.5, 0.5),
        BackgroundTransparency = 1,
        TextScaled  = true,
        Active      = true,
        Text        = default or "",
        PlaceholderText = placeholder,
        Font        = theme.Font.Bold,
        TextColor3  = theme.Text.Default,
        Parent      = boxFrame,
    })

    local icon = New("ImageLabel", {
        Size        = UDim2.new(0, 12, 0, 12),
        Position    = UDim2.new(0, -5, 0.5, 0),
        AnchorPoint = Vector2.new(1, 0.5),
        BackgroundTransparency = 1,
        Image       = theme.Icons.TextBox,
        ImageColor3 = theme.Icons,
        Parent      = boxFrame,
    })

    if clearOnFocus ~= nil then
        textBox.ClearTextOnFocus = clearOnFocus
    end

    local element = setmetatable({
        Title        = title,
        Description  = config.Description or "",
        Kind         = "TextBox",
        Callbacks    = callbacks,
        RootFrame    = rootButton,
        VisibleFrame = rootButton,
        TitleLabel   = titleLabel,
        DescLabel    = descLabel,
        TextBox      = textBox,
        Parent       = self,

        _textFilter  = nil,
    }, ElementBase)

    function element:SetText(text)
        assert(type(text) == "string", "TextBox.SetText: string expected")
        textBox.Text = text
        return self
    end

    function element:SetPlaceholder(text)
        assert(type(text) == "string", "TextBox.SetPlaceholder: string expected")
        textBox.PlaceholderText = text
        return self
    end

    function element:CaptureFocus()
        textBox:CaptureFocus()
        return self
    end

    function element:Clear()
        textBox.Text = ""
        return self
    end

    function element:SetTextFilter(fn)
        assert(fn == nil or type(fn) == "function", "SetTextFilter: function or nil expected")
        self._textFilter = fn
        return self
    end

    element.Set = element.SetText

    if flag then
        Connect(textBox:GetPropertyChangedSignal("Text"), function()
            Library.Options[flag] = textBox.Text
        end)
    end

    Connect(textBox.Focused, function()
        Tween(icon, "ImageColor3", theme.Primary, 0.5):Play()
    end)

    Connect(textBox.FocusLost, function()
        Tween(icon, "ImageColor3", theme.Icons, 0.5):Play()

        if element._textFilter then
            local filtered = element._textFilter(textBox.Text)
            if type(filtered) == "string" then
                textBox.Text = filtered
            end
        end

        FireCallbacks(callbacks, textBox.Text)
    end)

    Connect(rootButton.Activated, function()
        textBox:CaptureFocus()
    end)

    return element
end

function Tab:AddDropdown(config)
    assert(type(config) == "table", "AddDropdown: table expected")

    local title       = config[1] or config.Title or config.Name or "Dropdown"
    local options     = config[2] or config.Options or {}
    local default     = config[3] or config.Default
    local callback    = config[4] or config.Callback
    local flag        = config[5] or config.Flag
    local multiSelect = config.MultiSelect

    local theme     = Library.CurrentTheme
    local callbacks = callback and { callback } or {}

    if flag and type(Library.Options[flag]) == (multiSelect and "table" or "string") then
        default = Library.Options[flag]
    end

    local rootButton, titleLabel, descLabel = BuildOptionRow(
        self._container, theme,
        title, config.Description or config.Desc or "",
        UDim2.new(0, 150, 0, 0)
    )

    local displayFrame = New("Frame", {
        Size        = UDim2.new(0, 150, 0, 18),
        Position    = UDim2.new(1, -10, 0.5, 0),
        AnchorPoint = Vector2.new(1, 0.5),
        BackgroundColor3 = theme.Stroke,
        Parent      = rootButton,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0, 4) }),
        }
    })

    local displayLabel = New("TextLabel", {
        Size        = UDim2.new(0.85, 0, 0.85, 0),
        AnchorPoint = Vector2.new(0.5, 0.5),
        Position    = UDim2.fromScale(0.5, 0.5),
        BackgroundTransparency = 1,
        TextScaled  = true,
        Text        = "...",
        Font        = theme.Font.Bold,
        TextColor3  = theme.Text.Default,
        Parent      = displayFrame,
    })

    local arrowIcon = New("ImageLabel", {
        Size        = UDim2.new(0, 15, 0, 15),
        Position    = UDim2.new(0, -5, 0.5, 0),
        AnchorPoint = Vector2.new(1, 0.5),
        BackgroundTransparency = 1,
        Image       = theme.Icons.Dropdown.Open,
        ImageColor3 = theme.Icons,
        Parent      = displayFrame,
    })

    -- Option data
    local allOptions    = {}  -- { Name, DisplayName, Selected, Instance }
    local optionByName  = {}
    local selectedMap   = {}  -- for multi: name -> bool; for single: current option
    local currentSingle = nil -- single-select only

    local isOpen    = false
    local dropFrame = nil  -- the floating dropdown frame (created on first open)

    local element = setmetatable({
        Title        = title,
        Description  = config.Description or "",
        Kind         = "Dropdown",
        Callbacks    = callbacks,
        RootFrame    = rootButton,
        VisibleFrame = rootButton,
        TitleLabel   = titleLabel,
        DescLabel    = descLabel,
        Parent       = self,
        Opened       = false,
        DROPDOWN_OPTIONS = allOptions,
    }, ElementBase)

    local function updateDisplay()
        local text
        if multiSelect then
            local selected = {}
            for name, sel in selectedMap do
                if sel then table.insert(selected, name) end
            end
            text = table.concat(selected, ", ")
        else
            text = currentSingle and currentSingle.Name or ""
        end
        if #text > 100 then text = text:sub(1, 97) .. "..." end
        displayLabel.Text = #text > 0 and text or "..."
    end

    local function fireCallback()
        if multiSelect then
            FireCallbacks(callbacks, selectedMap)
            if flag then Library.Options[flag] = selectedMap end
        else
            local name = currentSingle and currentSingle.Name or ""
            FireCallbacks(callbacks, name)
            if flag then Library.Options[flag] = name end
        end
        updateDisplay()
    end

    local function selectOption(option)
        if multiSelect then
            selectedMap[option.Name] = not selectedMap[option.Name]
        else
            if currentSingle then currentSingle.Selected = false end
            currentSingle = option
            option.Selected = true
        end
        task.defer(fireCallback)
    end

    local function closeDropdown()
        if not isOpen or not dropFrame then return end
        isOpen = false
        element.Opened = false
        arrowIcon.Image = theme.Icons.Dropdown.Open
        Tween(arrowIcon, "ImageColor3", theme.Icons, 0.3):Play()
        dropFrame:Destroy()
        dropFrame = nil
    end

    local function openDropdown()
        if isOpen then return end
        isOpen = true
        element.Opened = true
        arrowIcon.Image = theme.Icons.Dropdown.Close
        Tween(arrowIcon, "ImageColor3", theme.Primary, 0.3):Play()

        dropFrame = New("Frame", {
            Size        = UDim2.fromOffset(160, 10),
            BackgroundColor3 = theme.Buttons.Default,
            BorderSizePixel = 0,
            ZIndex      = 10,
            Parent      = displayFrame,
            Position    = UDim2.new(0, 0, 1, 4),
            Children = {
                New("UICorner",  { CornerRadius = UDim.new(0, 6) }),
                New("UIStroke",  { Color = theme.Stroke, Thickness = 1 }),
            }
        })

        local listFrame = New("ScrollingFrame", {
            Size        = UDim2.new(1, -6, 1, -6),
            Position    = UDim2.fromScale(0.5, 0.5),
            AnchorPoint = Vector2.new(0.5, 0.5),
            ScrollBarThickness = 3,
            BackgroundTransparency = 1,
            BorderSizePixel = 0,
            CanvasSize  = UDim2.new(),
            AutomaticCanvasSize = Enum.AutomaticSize.Y,
            ScrollingDirection = Enum.ScrollingDirection.Y,
            Parent      = dropFrame,
            Children = {
                New("UIPadding", {
                    PaddingLeft   = UDim.new(0, 8),
                    PaddingRight  = UDim.new(0, 8),
                    PaddingTop    = UDim.new(0, 5),
                    PaddingBottom = UDim.new(0, 5),
                }),
                New("UIListLayout", { Padding = UDim.new(0, 4) }),
            }
        })

        -- Build option buttons
        for _, opt in allOptions do
            local optBtn = New("TextButton", {
                Size        = UDim2.new(1, 0, 0, 21),
                AutoButtonColor = false,
                Text        = "",
                BackgroundColor3 = theme.Buttons.Default,
                Parent      = listFrame,
                Children = {
                    New("UICorner", { CornerRadius = UDim.new(0, 4) }),
                    New("Frame", {
                        Position    = UDim2.new(0, 1, 0.5, 0),
                        Size        = UDim2.fromOffset(4, opt.Selected and 14 or 4),
                        AnchorPoint = Vector2.new(0, 0.5),
                        BackgroundColor3 = theme.Primary,
                        BackgroundTransparency = opt.Selected and 0 or 1,
                        Children = {
                            New("UICorner", { CornerRadius = UDim.new(0.5, 0) }),
                        }
                    }),
                    New("TextLabel", {
                        Size        = UDim2.fromScale(1, 1),
                        Position    = UDim2.fromOffset(10, 0),
                        TextXAlignment = Enum.TextXAlignment.Left,
                        BackgroundTransparency = 1,
                        TextTransparency = opt.Selected and 0 or 0.4,
                        Text        = opt.DisplayName,
                        TextSize    = 9,
                        Font        = theme.Font.Bold,
                        TextColor3  = theme.Text.Default,
                    })
                }
            })

            opt.Instance = optBtn

            Connect(optBtn.Activated, function()
                selectOption(opt)
                if not multiSelect then
                    closeDropdown()
                end
            end)
        end

        -- Resize dropdown to fit options
        local optCount = #allOptions
        local itemHeight = 25
        local maxHeight  = math.min(optCount * itemHeight + 10, 200)
        Tween(dropFrame, "Size", UDim2.fromOffset(160, math.max(maxHeight, 30)), 0.2):Play()

        -- Close on outside click
        local outsideConn
        outsideConn = Connect(UserInputService.InputBegan, function(input)
            if input.UserInputType ~= Enum.UserInputType.MouseButton1 then return end
            local absPos  = displayFrame.AbsolutePosition
            local absSize = displayFrame.AbsoluteSize
            local mx, my  = Mouse.X, Mouse.Y
            local insideDisplay = mx >= absPos.X and mx <= absPos.X + absSize.X
                and my >= absPos.Y and my <= absPos.Y + absSize.Y

            if not isOpen then
                outsideConn:Disconnect()
                return
            end

            if not insideDisplay then
                closeDropdown()
                outsideConn:Disconnect()
            end
        end)
    end

    -- Add an option
    local function addOption(name)
        name = tostring(name)
        if optionByName[name] then return end

        local opt = {
            Name        = name,
            DisplayName = name,
            Selected    = false,
            Instance    = nil,
        }

        if multiSelect then selectedMap[name] = false end

        optionByName[name] = opt
        table.insert(allOptions, opt)
        return opt
    end

    -- Public API
    function element:Add(...)
        for _, name in { ... } do
            addOption(name)
        end
    end

    function element:Remove(...)
        for _, name in { ... } do
            local opt = optionByName[tostring(name)]
            if opt then
                local idx = table.find(allOptions, opt)
                if idx then table.remove(allOptions, idx) end
                if opt.Instance then opt.Instance:Destroy() end
                optionByName[name] = nil
            end
        end
    end

    function element:Clear()
        for i = #allOptions, 1, -1 do
            local opt = allOptions[i]
            if opt.Instance then opt.Instance:Destroy() end
            optionByName[opt.Name] = nil
            allOptions[i] = nil
        end
        currentSingle = nil
        for k in selectedMap do selectedMap[k] = nil end
        updateDisplay()
    end

    function element:NewOptions(...)
        self:Clear()
        self:Add(...)
    end

    function element:SetEnabled(t)
        assert(type(t) == "table", "Dropdown.SetEnabled: table expected")
        for name, enabled in t do
            local opt = optionByName[tostring(name)]
            if opt and opt.Instance then
                opt.Instance.Visible = enabled
            end
        end
    end

    function element:GetOptionsCount()
        return #allOptions
    end

    element.Set = element.SetEnabled

    -- Seed options
    for _, name in options do
        addOption(name)
    end

    -- Apply default
    if type(default) == "string" then
        local opt = optionByName[default]
        if opt then
            opt.Selected  = true
            currentSingle = opt
        end
    elseif type(default) == "table" then
        for _, name in default do
            local opt = optionByName[tostring(name)]
            if opt then
                opt.Selected       = true
                selectedMap[name]  = true
            end
        end
    end

    task.defer(fireCallback)

    Connect(rootButton.Activated, function()
        if isOpen then closeDropdown() else openDropdown() end
    end)

    return element
end

function Tab:AddParagraph(title, body)
    assert(type(title) == "string", "AddParagraph: string expected for title")

    local theme = Library.CurrentTheme
    local rootButton, titleLabel, descLabel = BuildOptionRow(
        self._container, theme,
        title, body or "",
        UDim2.new(0, 0, 0, 0)
    )

    local element = setmetatable({
        Title        = title,
        Description  = body or "",
        Kind         = "Paragraph",
        RootFrame    = rootButton,
        VisibleFrame = rootButton,
        TitleLabel   = titleLabel,
        DescLabel    = descLabel,
        Parent       = self,
    }, ElementBase)

    return element
end

function Tab:AddDiscordInvite(config)
    assert(type(config) == "table", "AddDiscordInvite: table expected")

    local title   = config[1] or config.Title or config.Name or "Discord"
    local desc    = config[2] or config.Description or config.Desc
    local icon    = config.Icon or config.Image or config.Logo
    local banner  = config.Banner or config.BannerColor
    local online  = config.Online or config.MembersOnline
    local members = config.Members or config.TotalMembers
    local invite  = config.Invite or config.Link

    assert(type(invite) == "string", "AddDiscordInvite.Invite: string expected")

    local theme = Library.CurrentTheme

    local outerFrame = New("Frame", {
        Name = "DiscordInvite",
        BackgroundTransparency = 1,
        Size = UDim2.new(1, 0, 0, 148),
        Parent = self._container,
    })

    local card = New("CanvasGroup", {
        Size        = UDim2.new(0, 178, 1, -15),
        Position    = UDim2.new(0, 5, 1, 0),
        AnchorPoint = Vector2.new(0, 1),
        ClipsDescendants = true,
        BackgroundColor3 = theme.Buttons.Default,
        Parent      = outerFrame,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0, 9) }),
            New("UIStroke", { Color = theme.Border.Default }),
        }
    })

    -- Banner
    local bannerFrame = New("ImageLabel", {
        BackgroundColor3 = Color3.new(1, 1, 1),
        Size        = UDim2.fromScale(1, 0.28),
        BackgroundTransparency = 1,
        Parent      = card,
    })

    -- Link label
    New("TextLabel", {
        Position    = UDim2.fromOffset(5, 0),
        Size        = UDim2.new(1, 0, 0, 15),
        TextXAlignment = Enum.TextXAlignment.Left,
        BackgroundTransparency = 1,
        TextSize    = 9,
        Text        = invite,
        Font        = theme.Font.Medium,
        TextColor3  = theme.Link,
        Parent      = outerFrame,
    })

    -- Server icon
    New("ImageLabel", {
        Size        = UDim2.fromOffset(33, 33),
        Position    = UDim2.new(0, 10, 0.28, 0),
        AnchorPoint = Vector2.new(0, 0.5),
        Image       = icon or "",
        BackgroundColor3 = theme.Buttons.Default,
        Parent      = card,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0, 8) }),
            New("UIStroke", { Thickness = 2.2, ApplyStrokeMode = Enum.ApplyStrokeMode.Border, Color = theme.Buttons.Default }),
        }
    })

    -- Server name
    local titleLabel = New("TextLabel", {
        Size        = UDim2.new(1, -10, 0, 10),
        Position    = UDim2.new(0, 10, 0.44, 0),
        TextXAlignment = Enum.TextXAlignment.Left,
        BackgroundTransparency = 1,
        TextSize    = 11,
        Text        = title,
        Font        = theme.Font.Bold,
        TextColor3  = theme.Text.Default,
        Parent      = card,
    })

    -- Member counts
    if online or members then
        local countsRow = New("Frame", {
            Size        = UDim2.new(1, -10, 0, 9),
            Position    = UDim2.new(0, 0, 0.52, 0),
            BackgroundTransparency = 1,
            Parent      = card,
            Children = {
                New("UIPadding", {
                    PaddingLeft  = UDim.new(0, 7),
                    PaddingRight = UDim.new(0, 10),
                }),
                New("UIListLayout", {
                    HorizontalAlignment = Enum.HorizontalAlignment.Left,
                    VerticalAlignment   = Enum.VerticalAlignment.Center,
                    FillDirection       = Enum.FillDirection.Horizontal,
                    Padding             = UDim.new(0, 4),
                }),
            }
        })

        local function addCount(color, text)
            New("Frame", {
                Size        = UDim2.fromScale(0, 1),
                AutomaticSize = Enum.AutomaticSize.X,
                BackgroundTransparency = 1,
                Parent      = countsRow,
                Children = {
                    New("Frame", {
                        Size        = UDim2.fromOffset(3, 3),
                        Position    = UDim2.new(0, 5, 0.5, 0),
                        AnchorPoint = Vector2.new(0, 0.5),
                        BackgroundColor3 = color,
                        Children = { New("UICorner", { CornerRadius = UDim.new(1, 0) }) }
                    }),
                    New("TextLabel", {
                        Size        = UDim2.new(0, 0, 1, 0),
                        Position    = UDim2.new(0, 12, 0.5, 0),
                        AnchorPoint = Vector2.new(0, 0.5),
                        AutomaticSize = Enum.AutomaticSize.X,
                        BackgroundTransparency = 1,
                        TextSize    = 7,
                        Text        = text,
                        Font        = theme.Font.Normal,
                        TextColor3  = theme.Text.Darker,
                    }),
                }
            })
        end

        if online  then addCount(Color3.fromRGB(67, 181, 129), FormatNumber(online)  .. " Online")  end
        if members then addCount(Color3.fromRGB(86, 101, 105), FormatNumber(members) .. " Members") end
    end

    -- Description
    local descLabel = New("TextLabel", {
        Size        = UDim2.new(1, -50, 0, 8),
        Position    = UDim2.new(0, 10, (online or members) and 0.6 or 0.56, 0),
        TextXAlignment = Enum.TextXAlignment.Left,
        AutomaticSize = Enum.AutomaticSize.Y,
        BackgroundTransparency = 1,
        TextSize    = 8,
        Text        = desc or "",
        TextWrapped = true,
        Font        = theme.Font.Medium,
        TextColor3  = theme.Text.Darker,
        Parent      = card,
    })

    -- Bottom gradient + button
    local bottomGrad = New("Frame", {
        Size        = UDim2.new(1, 0, #(desc or "") > 0 and 0.42 or 0.28, 0),
        Position    = UDim2.fromScale(0, 1),
        AnchorPoint = Vector2.new(0, 1),
        BorderSizePixel = 0,
        BackgroundColor3 = theme.Buttons.Default,
        Parent      = card,
    })

    if #(desc or "") > 0 then
        New("UIGradient", {
            Rotation    = -90,
            Transparency = NumberSequence.new({
                NumberSequenceKeypoint.new(0.0, 0.0),
                NumberSequenceKeypoint.new(0.6, 0.0),
                NumberSequenceKeypoint.new(1.0, 1.0),
            }),
            Parent = bottomGrad,
        })
    end

    local joinBtn = New("TextButton", {
        Position    = UDim2.new(0.5, 0, 1, -9),
        Size        = UDim2.new(1, -18, 0, 18),
        AnchorPoint = Vector2.new(0.5, 1),
        Text        = "Go to Server",
        BackgroundColor3 = theme.JoinButton,
        Font        = theme.Font.Bold,
        TextColor3  = theme.Text.Default,
        Parent      = bottomGrad,
        Children = { New("UICorner", { CornerRadius = UDim.new(0.5, 0) }) }
    })

    -- Apply banner
    if type(banner) == "string" then
        bannerFrame.ScaleType = Enum.ScaleType.Crop
        bannerFrame.Image     = banner
        bannerFrame.BackgroundTransparency = 1
    elseif typeof(banner) == "Color3" then
        bannerFrame.BackgroundTransparency = 0
        bannerFrame.BackgroundColor3 = banner
    end

    local lastClick = 0
    Connect(joinBtn.Activated, function()
        if (tick() - lastClick) < 5 then return end
        lastClick = tick()
        local original = joinBtn.Text
        joinBtn.Text = "Copied!"
        if setclipboard then setclipboard(invite) end
        task.wait(4)
        joinBtn.Text = original
    end)

    local element = setmetatable({
        Title        = title,
        Description  = desc or "",
        Kind         = "DiscordInvite",
        RootFrame    = outerFrame,
        VisibleFrame = outerFrame,
        TitleLabel   = titleLabel,
        DescLabel    = descLabel,
        Parent       = self,
    }, ElementBase)

    return element
end

-- ============================================================
--  WINDOW CLASS
-- ============================================================

local Window = {}
Window.__index = Window

function Window:MakeTab(config)
    assert(type(config) == "table", "MakeTab: table expected")

    local title = config[1] or config.Title or config.Name or "Tab"
    local icon  = config[2] or config.Icon or config.Image

    assert(type(title) == "string", "MakeTab.Title: string expected")

    local theme     = Library.CurrentTheme
    local isFirst   = #self._tabs == 0

    -- Tab button in sidebar
    local indicator = New("Frame", {
        Position    = UDim2.new(0, 1, 0.5, 0),
        AnchorPoint = Vector2.new(0, 0.5),
        Size        = UDim2.fromOffset(4, 4),
        BackgroundTransparency = 1,
        BackgroundColor3 = theme.Primary,
        Children = { New("UICorner", { CornerRadius = UDim.new(0.5, 0) }) }
    })

    local iconLabel = New("ImageLabel", {
        Position    = UDim2.new(0, 8, 0.5, 0),
        Size        = UDim2.fromOffset(13, 13),
        AnchorPoint = Vector2.new(0, 0.5),
        BackgroundTransparency = 1,
        ImageTransparency = 0.3,
        Image       = Library:GetIconByName(icon) or "",
    })

    local hasIcon   = IsAssetId(iconLabel.Image)
    local titleLabel = New("TextLabel", {
        Name        = "Title",
        BackgroundTransparency = 1,
        Font        = Enum.Font.GothamMedium,
        Text        = title,
        TextSize    = 10,
        TextXAlignment = Enum.TextXAlignment.Left,
        TextTruncate   = Enum.TextTruncate.AtEnd,
        TextTransparency = isFirst and 0 or 0.3,
        Size        = UDim2.new(1, hasIcon and -25 or -15, 1, 0),
        Position    = UDim2.fromOffset(hasIcon and 25 or 15, 0),
        TextColor3  = theme.Text.Default,
    })

    local tabButton = New("TextButton", {
        Name        = "TabButton",
        Size        = UDim2.new(1, 0, 0, 24),
        AutoButtonColor = false,
        Text        = "",
        BackgroundColor3 = theme.Buttons.Default,
        Parent      = self._tabsScroll,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0, 6) }),
            indicator,
            iconLabel,
            titleLabel,
        }
    })

    iconLabel.Visible = hasIcon

    -- Tab content frame
    local contentFrame = New("ScrollingFrame", {
        Name                   = "TabContent",
        Size                   = UDim2.new(1, 0, 1, 0),
        BackgroundTransparency = 1,
        ScrollBarThickness     = 1.5,
        ScrollBarImageTransparency = 0.2,
        AutomaticCanvasSize    = Enum.AutomaticSize.Y,
        ScrollingDirection     = Enum.ScrollingDirection.Y,
        BorderSizePixel        = 0,
        CanvasSize             = UDim2.new(),
        ScrollBarImageColor3   = theme.ScrollBar,
        Children = {
            New("UIPadding", {
                PaddingLeft   = UDim.new(0, 10),
                PaddingRight  = UDim.new(0, 10),
                PaddingTop    = UDim.new(0, 10),
                PaddingBottom = UDim.new(0, 10),
            }),
            New("UIListLayout", { Padding = UDim.new(0, 5) }),
        }
    })

    local tab = setmetatable({
        Title          = title,
        Icon           = icon,
        Selected       = false,

        _window        = self,
        _tabButton     = tabButton,
        _indicator     = indicator,
        _contentFrame  = contentFrame,
        _container     = contentFrame,
    }, Tab)

    table.insert(self._tabs, tab)

    Connect(tabButton.Activated, function()
        tab:Select()
    end)

    if isFirst then
        tab:Select()
    end

    return tab
end

function Window:SelectTab(tabOrIndex)
    if type(tabOrIndex) == "number" then
        local t = self._tabs[tabOrIndex]
        if t then t:Select() end
    elseif type(tabOrIndex) == "table" then
        tabOrIndex:Select()
    end
end

function Window:Minimize()
    self._mainFrame.Visible = not self._mainFrame.Visible
end

function Window:SetTitle(text)
    assert(type(text) == "string" and #text > 0, "SetTitle: non-empty string expected")
    self._titleLabel.Text = text
end

function Window:SetSubTitle(text)
    assert(type(text) == "string" and #text > 0, "SetSubTitle: non-empty string expected")
    self._subtitleLabel.Text = text
end

function Window:GetTitle()    return self._titleLabel.Text    end
function Window:GetSubTitle() return self._subtitleLabel.Text end

function Window:GetTabByTitle(name)
    assert(type(name) == "string", "GetTabByTitle: string expected")
    for _, tab in self._tabs do
        if tab.Title == name then return tab end
    end
end

Window.GetTabByName = Window.GetTabByTitle

function Window:Dialog(config)
    assert(type(config) == "table", "Dialog: table expected")

    local title   = config.Title or config.Name   or "Dialog"
    local content = config.Content or config.Description or ""
    local opts    = config.Options or {}

    assert(type(title)   == "string", "Dialog.Title: string expected")
    assert(type(content) == "string", "Dialog.Content: string expected")
    assert(#opts > 0, "Dialog.Options: at least one option required")

    local theme = Library.CurrentTheme

    local overlay = New("TextButton", {
        Size        = UDim2.fromScale(1, 1),
        BackgroundColor3 = theme.Buttons.Default,
        BackgroundTransparency = 0.3,
        AutoButtonColor = false,
        Text        = "",
        ZIndex      = 20,
        Parent      = self._mainFrame,
    })

    New("UICorner", { CornerRadius = UDim.new(0, 8), Parent = overlay })

    local panel = New("Frame", {
        Size        = UDim2.new(0.35, 60, 0.20, 80),
        Position    = UDim2.fromScale(0.5, 0.5),
        AnchorPoint = Vector2.new(0.5, 0.5),
        BackgroundColor3 = theme.Dialog.Background,
        Active      = true,
        ZIndex      = 21,
        Parent      = overlay,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0, 6) }),
            New("UIGradient", {
                Rotation = 45,
                Color    = theme.Background,
            }),
        }
    })

    New("TextLabel", {
        Name        = "Title",
        Size        = UDim2.new(1, -20, 0, 20),
        Position    = UDim2.new(0.5, 0, 0, 28),
        AnchorPoint = Vector2.new(0.5, 0),
        BackgroundTransparency = 1,
        TextSize    = 15,
        Text        = title,
        Font        = theme.Font.ExtraBold,
        TextColor3  = theme.Text.Default,
        ZIndex      = 22,
        Parent      = panel,
    })

    New("TextLabel", {
        Name        = "Description",
        Position    = UDim2.new(0.5, 0, 0, 46),
        Size        = UDim2.new(1, -20, 0, 0),
        AnchorPoint = Vector2.new(0.5, 0),
        TextWrapped = true,
        TextSize    = 11,
        AutomaticSize = Enum.AutomaticSize.Y,
        BackgroundTransparency = 1,
        Text        = content,
        Font        = theme.Font.Medium,
        TextColor3  = theme.Text.Darker,
        ZIndex      = 22,
        Parent      = panel,
    })

    local optionsRow = New("Frame", {
        Name        = "Options",
        Size        = UDim2.new(1, -20, 0.15, 18),
        Position    = UDim2.new(0.5, 0, 1, -10),
        AnchorPoint = Vector2.new(0.5, 1),
        BackgroundTransparency = 1,
        ZIndex      = 22,
        Parent      = panel,
        Children = {
            New("UIListLayout", {
                HorizontalAlignment = Enum.HorizontalAlignment.Right,
                VerticalAlignment   = Enum.VerticalAlignment.Center,
                FillDirection       = Enum.FillDirection.Horizontal,
            }),
        }
    })

    local function closeDialog()
        overlay:Destroy()
    end

    for i = #opts, 1, -1 do
        local opt      = opts[i]
        local optTitle = opt[1] or opt.Title or opt.Name or "Option"
        local optCb    = opt[2] or opt.Callback

        local btn = New("TextButton", {
            AutoButtonColor = false,
            Size        = UDim2.fromScale(0.2, 1),
            BackgroundTransparency = 1,
            TextSize    = 10,
            Text        = optTitle,
            Font        = theme.Font.Normal,
            TextColor3  = theme.Text.Dark,
            ZIndex      = 23,
            Parent      = optionsRow,
            Children = { New("UICorner", { CornerRadius = UDim.new(1, 0) }) }
        })

        Connect(btn.MouseEnter, function()
            Tween(btn, "BackgroundTransparency", 0, 0.3):Play()
        end)
        Connect(btn.MouseLeave, function()
            Tween(btn, "BackgroundTransparency", 1, 0.3):Play()
        end)

        Connect(btn.Activated, function()
            closeDialog()
            if optCb then task.spawn(optCb) end
        end)
    end

    Connect(overlay.Activated, closeDialog)

    -- Animate in
    local origSize = panel.Size
    panel.Size = UDim2.new(origSize.X.Scale * 1.2, origSize.X.Offset, origSize.Y.Scale * 1.2, origSize.Y.Offset)
    Tween(panel, "Size", origSize, 0.3):Play()
end

function Window:Notify(config)
    if type(config) ~= "table" then config = {} end

    local title   = config[1] or config.Title or config.Name or "Notification"
    local content = config[2] or config.Content or ""
    local icon    = config[3] or config.Icon or config.Image
    local duration= config[4] or config.Duration or config.Time or 5

    assert(type(title)   == "string", "Notify.Title: string expected")
    assert(type(content) == "string", "Notify.Content: string expected")

    local theme = Library.CurrentTheme
    icon = Library:GetIconByName(icon)

    local notifFrame = New("Frame", {
        Name        = "Notification",
        Size        = UDim2.new(0.85, 0, 0, 60),
        BackgroundTransparency = 1,
        AutomaticSize = Enum.AutomaticSize.Y,
        Parent      = self._notifyHolder,
    })

    local card = New("TextButton", {
        AutomaticSize = Enum.AutomaticSize.Y,
        Size        = UDim2.fromScale(1, 1),
        AutoButtonColor = false,
        Text        = "",
        BackgroundTransparency = theme.BackgroundTransparency,
        BackgroundColor3 = theme.Buttons.Default,
        Parent      = notifFrame,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0, 9) }),
            New("UIGradient", {
                Rotation = 45,
                Color    = theme.Background,
            }),
        }
    })

    local scaleObj = New("UIScale", { Parent = notifFrame })

    local holder = New("Frame", {
        Name        = "Holder",
        AutomaticSize = Enum.AutomaticSize.Y,
        BackgroundTransparency = 1,
        Size        = UDim2.fromScale(1, 1),
        Parent      = card,
        Children = {
            New("UIListLayout", {
                SortOrder         = Enum.SortOrder.LayoutOrder,
                VerticalAlignment = Enum.VerticalAlignment.Center,
                Padding           = UDim.new(0, 4),
            }),
            New("UIPadding", {
                PaddingBottom = UDim.new(0, 8),
                PaddingTop    = UDim.new(0, 8),
                PaddingLeft   = UDim.new(0, icon and IsAssetId(icon) and 40 or 15),
            }),
        }
    })

    New("TextLabel", {
        Size        = UDim2.new(1, 0, 0, 20),
        TextTruncate  = Enum.TextTruncate.AtEnd,
        TextXAlignment = Enum.TextXAlignment.Left,
        TextYAlignment = Enum.TextYAlignment.Bottom,
        BackgroundTransparency = 1,
        TextSize    = 14,
        Text        = title,
        Font        = theme.Font.Bold,
        TextColor3  = theme.Text.Default,
        Parent      = holder,
    })

    New("TextLabel", {
        Size        = UDim2.new(1, 0, 0, 20),
        TextXAlignment = Enum.TextXAlignment.Left,
        TextYAlignment = Enum.TextYAlignment.Top,
        AutomaticSize = Enum.AutomaticSize.Y,
        BackgroundTransparency = 1,
        TextWrapped = true,
        TextSize    = 12,
        Text        = content,
        Font        = theme.Font.Normal,
        TextColor3  = theme.Text.Dark,
        Parent      = holder,
    })

    if icon and IsAssetId(icon) then
        New("ImageLabel", {
            Size        = UDim2.fromOffset(24, 24),
            Position    = UDim2.new(0, 8, 0.5, 0),
            AnchorPoint = Vector2.new(0, 0.5),
            BackgroundTransparency = 1,
            Image       = icon,
            ImageColor3 = theme.Icons,
            Parent      = card,
        })
    end

    local timeLabel = New("TextLabel", {
        Size        = UDim2.new(0, 40, 0, 16),
        Position    = UDim2.new(1, -10, 0, 8),
        AnchorPoint = Vector2.new(1, 0),
        BackgroundTransparency = 1,
        TextSize    = 10,
        Font        = theme.Font.Normal,
        TextColor3  = theme.Text.Darker,
        Parent      = card,
    })

    local paused = false

    local function closeNotif()
        local slideOut = Tween(card, "Position", UDim2.fromScale(3, 0), 0.8)
        slideOut:Play()
        slideOut.Completed:Wait()
        notifFrame:Destroy()
    end

    Connect(card.MouseButton1Down, function()
        Tween(scaleObj, "Scale", 1.22, 0.35):Play()
        paused = true
    end)

    Connect(card.MouseLeave, function()
        Tween(scaleObj, "Scale", 1.00, 0.35):Play()
        paused = false
    end)

    -- Slide in
    card.Position = UDim2.fromScale(3, 0)
    Tween(card, "Position", UDim2.fromScale(0, 0), 0.35):Play()

    task.spawn(function()
        local remaining = duration
        while remaining > 0 do
            timeLabel.Text = FormatTime(remaining)
            if paused then card.MouseLeave:Wait() end
            remaining -= task.wait()
        end
        closeNotif()
    end)

    local notifElement = setmetatable({
        Kind         = "Notification",
        RootFrame    = notifFrame,
        VisibleFrame = notifFrame,
        Closed       = false,
        Parent       = self,
    }, ElementBase)

    function notifElement:Close()
        if self.Closed then return end
        self.Closed = true
        closeNotif()
    end

    return notifElement
end

function Window:NewNotifyGroup(config)
    if type(config) ~= "table" then config = {} end

    return {
        NOTIFICATION_GROUP = true,
        Notify = Window.Notify,
        Title    = config[1] or config.Title,
        Content  = config[2] or config.Content,
        Icon     = config[3] or config.Icon,
        Duration = config[4] or config.Duration,
    }
end

Window.NewNotificationGroup  = Window.NewNotifyGroup
Window.Notification          = Window.Notify

function Window:NewMinimizer(keyCode)
    if type(keyCode) == "table" then
        keyCode = keyCode[1] or keyCode.KeyCode
    end

    assert(typeof(keyCode) == "EnumItem", "NewMinimizer: KeyCode EnumItem expected")

    Connect(UserInputService.InputBegan, function(input)
        if input.KeyCode == keyCode then
            self:Minimize()
        end
    end)

    return {
        KeyCode = keyCode,
        SetKeyCode = function(self, newKey)
            self.KeyCode = newKey
        end
    }
end

function Window:SetFlag(key, value)
    assert(type(key) == "string", "SetFlag: string key expected")
    Library.Options[key] = value
end

function Window:GetFlag(key)
    return Library.Options[key]
end

function Window:Destroy()
    for _, conn in Library.Connections do
        conn:Disconnect()
    end
    table.clear(Library.Connections)

    if self._screenGui then
        pcall(function() self._screenGui:Destroy() end)
    end
end

-- ============================================================
--  LIBRARY: MakeWindow
-- ============================================================

function Library:MakeWindow(config)
    assert(not self.Loaded, "MakeWindow: only one window can be created")
    assert(type(config) == "table", "MakeWindow: table expected")

    local title       = config[1] or config.Title or config.Name     or "UI"
    local subtitle    = config[2] or config.SubTitle or config.SubName or "Library"
    local folderName  = config[3] or config.ScriptFolder or config.FolderName

    assert(type(title)    == "string", "MakeWindow.Title: string expected")
    assert(type(subtitle) == "string", "MakeWindow.SubTitle: string expected")

    self.Loaded = true

    -- Set up theme
    self:SetTheme(self.Default.Theme)
    local theme = self.CurrentTheme

    -- Screen GUI
    local gui = (gethui or function() return game:GetService("CoreGui") end)()
    local screenGui = Instance.new("ScreenGui")
    screenGui.Name            = "RedzLibrary"
    screenGui.IgnoreGuiInset  = true
    screenGui.ResetOnSpawn    = false
    screenGui.ZIndexBehavior  = Enum.ZIndexBehavior.Sibling
    screenGui.Parent          = gui

    local uiScale = New("UIScale", {
        Scale  = ScaleToViewport(1),
        Parent = screenGui,
    })

    -- Main window frame
    local windowSize = self.Default.UISize
    local mainFrame  = New("Frame", {
        Name        = "Window",
        Position    = UDim2.new(0.5, -windowSize.X.Offset/2, 0.5, -windowSize.Y.Offset/2),
        Size        = windowSize,
        Active      = true,
        BackgroundColor3 = theme.Buttons.Default,
        BackgroundTransparency = theme.BackgroundTransparency,
        Parent      = screenGui,
        Children = {
            New("UICorner", { CornerRadius = UDim.new(0, 8) }),
            New("UIGradient", {
                Rotation = 45,
                Color    = theme.Background,
            }),
        }
    })

    MakeDraggable(mainFrame, uiScale, 0.5)

    -- Top bar
    local topBar = New("Frame", {
        Name        = "TopBar",
        Size        = UDim2.new(1, 0, 0, 28),
        BackgroundTransparency = 1,
        Parent      = mainFrame,
    })

    local titleLabel = New("TextLabel", {
        Name        = "Title",
        TextXAlignment = Enum.TextXAlignment.Left,
        AutomaticSize  = Enum.AutomaticSize.XY,
        Position    = UDim2.new(0, 15, 0.5, 0),
        AnchorPoint = Vector2.new(0, 0.5),
        Text        = title,
        TextSize    = 12,
        BackgroundTransparency = 1,
        Font        = theme.Font.Bold,
        TextColor3  = theme.Text.Default,
        Parent      = topBar,
    })

    local subtitleLabel = New("TextLabel", {
        Name        = "SubTitle",
        Size        = UDim2.fromScale(0, 1),
        AutomaticSize = Enum.AutomaticSize.X,
        AnchorPoint = Vector2.new(0, 1),
        Position    = UDim2.new(1, 5, 0.9, 0),
        Text        = subtitle,
        BackgroundTransparency = 1,
        TextXAlignment = Enum.TextXAlignment.Left,
        TextYAlignment = Enum.TextYAlignment.Bottom,
        TextSize    = 8,
        Font        = theme.Font.Normal,
        TextColor3  = theme.Text.Dark,
        Parent      = titleLabel,
    })

    -- Close & Minimize buttons
    local closeBtn = New("ImageButton", {
        Name        = "Close",
        Size        = UDim2.fromOffset(18, 18),
        Position    = UDim2.new(1, -10, 0.5, 0),
        AnchorPoint = Vector2.new(1, 0.5),
        BackgroundTransparency = 1,
        BackgroundColor3 = Color3.fromRGB(255, 35, 35),
        AutoButtonColor = false,
        Image       = theme.Icons.Close,
        Parent      = topBar,
        Children    = { New("UICorner", { CornerRadius = UDim.new(0.2, 0) }) }
    })

    local minimizeBtn = New("ImageButton", {
        Name        = "Minimize",
        Size        = UDim2.fromOffset(18, 18),
        Position    = UDim2.new(1, -35, 0.5, 0),
        AnchorPoint = Vector2.new(1, 0.5),
        BackgroundTransparency = 1,
        AutoButtonColor = false,
        Image       = "rbxassetid://10734896206",
        Parent      = topBar,
        Children    = { New("UICorner", { CornerRadius = UDim.new(0.2, 0) }) }
    })

    -- Hover effects on buttons
    for _, btn in { closeBtn, minimizeBtn } do
        Connect(btn.MouseEnter, function()  btn.BackgroundTransparency = 0.65 end)
        Connect(btn.MouseLeave, function()  btn.BackgroundTransparency = 1.00 end)
    end

    -- Tab sidebar
    local tabSize  = self.Default.TabSize
    local tabsScroll = New("ScrollingFrame", {
        Name        = "TabsSidebar",
        Size        = UDim2.new(0, tabSize, 1, -topBar.Size.Y.Offset),
        Position    = UDim2.new(0, 0, 1, 0),
        AnchorPoint = Vector2.new(0, 1),
        AutomaticCanvasSize    = Enum.AutomaticSize.Y,
        ScrollingDirection     = Enum.ScrollingDirection.Y,
        ScrollBarThickness     = 2.2,
        BackgroundTransparency = 1,
        ScrollBarImageTransparency = 0.2,
        CanvasSize  = UDim2.new(),
        BorderSizePixel = 0,
        ScrollBarImageColor3 = theme.ScrollBar,
        Parent      = mainFrame,
        Children = {
            New("UIPadding", {
                PaddingLeft   = UDim.new(0, 10),
                PaddingRight  = UDim.new(0, 10),
                PaddingTop    = UDim.new(0, 10),
                PaddingBottom = UDim.new(0, 10),
            }),
            New("UIListLayout", { Padding = UDim.new(0, 5) }),
        }
    })

    -- Container holder (right side)
    local containerHolder = New("Frame", {
        Name        = "ContainerHolder",
        Size        = UDim2.new(1, -tabSize, 1, -topBar.Size.Y.Offset),
        Position    = UDim2.new(1, 0, 1, 0),
        AnchorPoint = Vector2.new(1, 1),
        BackgroundTransparency = 1,
        ClipsDescendants = true,
        Parent      = mainFrame,
    })

    -- Notification holder
    local notifyHolder = New("Frame", {
        Name        = "NotifyHolder",
        Size        = UDim2.new(0, 280, 1, 0),
        Position    = UDim2.fromScale(1, 0),
        AnchorPoint = Vector2.new(1, 0),
        BackgroundTransparency = 1,
        Parent      = screenGui,
        Children = {
            New("UIPadding", { PaddingBottom = UDim.new(0, 20) }),
            New("UIListLayout", {
                HorizontalAlignment = Enum.HorizontalAlignment.Center,
                VerticalAlignment   = Enum.VerticalAlignment.Bottom,
                SortOrder           = Enum.SortOrder.LayoutOrder,
                Padding             = UDim.new(0, 20),
            }),
        }
    })

    -- Build window object
    local window = setmetatable({
        _screenGui      = screenGui,
        _mainFrame      = mainFrame,
        _topBar         = topBar,
        _tabsScroll     = tabsScroll,
        _containerHolder= containerHolder,
        _notifyHolder   = notifyHolder,
        _titleLabel     = titleLabel,
        _subtitleLabel  = subtitleLabel,
        _tabs           = {},
        _selectedTab    = nil,

        ScriptFolder    = folderName,
    }, Window)

    -- Close button -> dialog
    Connect(closeBtn.Activated, function()
        window:Dialog({
            Title   = "Close Window?",
            Content = "Are you sure you want to close the UI?",
            Options = {
                { Title = "Yes", Callback = function() window:Destroy() end },
                { Title = "No"  },
            }
        })
    end)

    -- Minimize button
    Connect(minimizeBtn.Activated, function()
        window:Minimize()
    end)

    return window
end

-- ============================================================
--  LIBRARY: Theme API
-- ============================================================

function Library:SetTheme(name)
    assert(type(name) == "string", "SetTheme: string expected")
    local t = self.Themes[name]
    assert(t, "SetTheme: theme not found: " .. name)
    self.CurrentTheme = t
end

function Library:GetTheme(name)
    if name == nil then return self.CurrentTheme end
    local t = self.Themes[name]
    assert(t, "GetTheme: theme not found: " .. name)
    return t
end

function Library:GetThemes()
    local list = {}
    for name in self.Themes do table.insert(list, name) end
    return list
end

function Library:IsValidTheme(name)
    return self.Themes[name] ~= nil
end

function Library:Destroy()
    for _, conn in self.Connections do conn:Disconnect() end
    table.clear(self.Connections)
end

-- ============================================================
--  RETURN
-- ============================================================

return Library
