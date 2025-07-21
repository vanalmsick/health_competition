import {useEffect, useState} from 'react'
import {QRCodeSVG} from 'qrcode.react';
import {usersApi} from "../utils/reducers/usersSlice";
import {useDispatch} from "react-redux";
import {workoutsApi} from "../utils/reducers/workoutsSlice";

const steps = [
    {title: "Welcome", content: "Let's find out how to best navigate the Health Competition!", img: null},
    {
        title: "Navigation",
        content: "At the top, switch between your personal (private) and competition (public) dashboards.",
        img: "/how_to_screen_1.png"
    },
    {
        title: "Your Profile",
        content: "See your lifetime stats, as well as change profile and privacy settings here.",
        img: "/how_to_screen_2.png"
    },
    {
        title: "Last 30 Day Stats",
        content: "See your personal stats and streak over the last 30 days.",
        img: "/how_to_screen_3.png"
    },
    {
        title: "Your 7 Day Personal Goals",
        content: "See and change your rolling 7 day activity goals.",
        img: "/how_to_screen_4.png"
    },
    {
        title: "Your Workouts",
        content: "Add manually or automatically via Strava your workouts.",
        img: "/how_to_screen_5.png"
    },
    {
        title: "Your Competitions",
        content: "Create your own or join other people's competitions.",
        img: "/how_to_screen_6.png"
    },
]

export function HowToScreen({setModal}) {
    const [current, setCurrent] = useState(0)

    return (
        <div className="fixed inset-0 z-50 bg-white bg-opacity-80 dark:bg-black dark:bg-opacity-80 flex items-center justify-center">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 max-w-2xl w-full text-center space-y-4">
                <h2 className="text-xl font-semibold">{steps[current].title}</h2>
                <p className="text-gray-600 dark:text-gray-400">{steps[current].content}</p>
                <img src={steps[current].img}/>
                <div className="flex justify-between mt-6">
                    <button
                        className="text-sm text-gray-500"
                        onClick={() => {
                            if (current === 0) {
                                setModal(false); // Close the modal
                                //setLinkStrava(true); // Open Strava link screen
                            } else {
                                setCurrent((c) => Math.max(0, c - 1));  // Go to previous step
                            }
                        }
                        }
                    >
                        {current === 0 ? 'Skip' : 'Back'}
                    </button>
                    <button
                        className="bg-blue-600 text-white px-4 py-2 rounded-full disabled:opacity-50"
                        onClick={() => {
                            if (current === steps.length - 1) {
                                setModal(false); // Close the modal
                                //setLinkStrava(true); // Open Strava link screen
                            } else {
                                setCurrent((c) => Math.min(steps.length - 1, c + 1)); // Go to next step
                            }
                        }}
                    >
                        {current === steps.length - 1 ? 'Finish' : 'Next'}
                    </button>
                </div>
            </div>
        </div>
    )
}


export function LinkStravaScreen({setModal}) {
    const [current, setCurrent] = useState(0)
    const domain = window.location.origin;
    const url = domain + '/strava/link/';

    const dispatch = useDispatch();

    function refreshWorkouts() {
        dispatch(workoutsApi.util.invalidateTags(['Workout']));
        dispatch(usersApi.util.invalidateTags(['User']));
    }

    return (
        <div className="fixed inset-0 z-50 bg-white bg-opacity-80 dark:bg-black dark:bg-opacity-80 flex items-center justify-center">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 max-w-2xl w-full text-center space-y-4">
                {
                    current === 0 ? (
                        <>
                            <h2 className="text-xl font-semibold">Automatic workout import via Strava</h2>
                            <p className="text-gray-600 dark:text-gray-400">Either manually enter your workouts or link your free Strava
                                account for automatic workout import.</p>
                            <img src="/how_to_strava_sync.png"/>
                            <p>Only absolutely necessary metrics are synced with Strava:</p>
                            <ul>
                                <li>• Sport type</li>
                                <li>• Start time & duration</li>
                                <li>• Workout id</li>
                                <li>• Distance, kcal, kj, avg. watt</li>
                                <li>––– That's it – nothing more! –––</li>
                            </ul>
                        </>
                    ) : (
                        <>
                            <h2 className="text-xl font-semibold">Scan this QR Code to link Strava</h2>
                            <p className="text-gray-600 dark:text-gray-400">For automatic workout import link your Strava account via the
                                scanning the below QR code on your phone (that has the Strava App installed).</p>
                            <div className="flex justify-center items-center">
                                <QRCodeSVG value={url} title={"QR code to link to Strava account"} size={200}
                                           level={"L"}/>
                            </div>
                            <p className="text-gray-600 dark:text-gray-400">Or <a className="text-blue-500 hover:underline" href={url}
                                                               target="_blank">click this link</a></p>
                        </>
                    )
                }
                <div className="flex justify-between mt-6">
                    <button className="text-sm text-gray-500"
                            onClick={() => {
                                if (current === 0) {
                                    setModal(false); // Close the modal
                                } else {
                                    setCurrent(0); // Go to previous step
                                }
                            }}
                    >
                        {current === 0 ? 'Close without linking' : 'Back'}
                    </button>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-full"
                            onClick={() => {
                                if (current === 1) {
                                    setModal(false); // Close the modal
                                    refreshWorkouts(); // refresh workouts in case Strava was linked on phone via QR code
                                } else {
                                    setCurrent(1); // Go to next step
                                }
                            }}
                    >
                        {current === 1 ? 'Close' : "Let\'s link Strava"}
                    </button>
                </div>
            </div>
        </div>
    )
}
