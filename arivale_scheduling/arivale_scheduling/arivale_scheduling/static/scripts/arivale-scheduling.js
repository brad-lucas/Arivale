arivale = {
    global: {
        initialize: function () {
            arivale.global._setUpExpandables();
        },
        _setUpExpandables: function () {
            var $expandables = $('.expandable');
            $expandables.siblings().hide();
            $expandables.click(function toggleListView() {
                $(this).siblings().slideToggle(250, function performToggle() { });
            });
        }
    },
    helpers: {
        getAppointmentStartDateFromDisplayText: function ($obj, dateTimeSelector) {
            var startTime = (dateTimeSelector ? $obj.find(dateTimeSelector) : $obj).text().trim().split('-')[0].trim().replace(':', ''),
                splitDateAndTime = startTime.split(' '),
                date = splitDateAndTime[0],
                splitTime = splitDateAndTime[1].split(':');

            if (splitTime[1].endsWith('PM')) {
                var hour = parseInt(splitTime[0]);
                if (hour < 12) {
                    splitTime[0] = (hour + 12).toString();
                }
            }

            splitTime[1] = splitTime[1].substring(0, splitTime[1].length - 2);

            return new Date(date + ' ' + splitTime[0] + ':' + splitTime[1]);
        },
        addTimeSlotInOrder: function ($slots, slotSelector, $newSlot, dateTimeSelector) {
            // only operate on direct children
            var slotItems = $slots.find('>' + slotSelector);

            var insertionIndex = -1;
            if (slotItems.length > 0) {
                var newStartDateTime = arivale.helpers.getAppointmentStartDateFromDisplayText($newSlot, dateTimeSelector);

                for (var i = 0; i < slotItems.length; i++) {
                    var slotItemStartDateTime = arivale.helpers.getAppointmentStartDateFromDisplayText($(slotItems[i], dateTimeSelector));
                    if (newStartDateTime < slotItemStartDateTime) {
                        insertionIndex = i;
                        break;
                    }
                }
            }

            // if it hasn't been fit to insert, simply append to the end
            var slotToInsert = $newSlot[0];
            if (insertionIndex === -1) {
                slotItems.push(slotToInsert);
            } else {
                slotItems.splice(insertionIndex, 0, slotToInsert);
            }
            
            var nonSlotItems = $slots.find('> :not(' + slotSelector + ')');
            if (nonSlotItems) {
                for (var i = nonSlotItems.length - 1; i >= 0; i--) {
                    slotItems.splice(0, 0, nonSlotItems[i]);
                }
            }

            $slots.html(slotItems);
        },
        addUpcomingAvailability: function ($obj) {
            var $upcomingAvailability = $('#upcoming-availability'),
                $noUnbookedSlots = $upcomingAvailability.find('#no-unbooked-appointments');

            if ($noUnbookedSlots && !$noUnbookedSlots.hasClass('hidden')) {
                $noUnbookedSlots.addClass('hidden');
            }

            arivale.helpers.setUpCancelUpcomingAvailabilityButton($obj.find('button'));

            arivale.helpers.addTimeSlotInOrder($upcomingAvailability, '.upcoming-appointment', $obj, '.display-text');

            return $upcomingAvailability;
        },
        setUpCancelUpcomingAvailabilityButton: function ($buttonObj) {
            $buttonObj.click(function cancelBookedAppointment() {
                var $this = $(this),
                    $parent = $this.parent(),
                    $newSpan = $('<span />'),
                    somethingHappenedClass = 'something-happened';

                $parent.find('span.' + somethingHappenedClass).remove();

                var appointmentDeleted = function () {
                    $parent.html($newSpan.text('Appointment deleted.').html());
                    setTimeout(function removeText() {
                        $parent.remove();
                        if ($('.upcoming-appointment').length === 0) {
                            $('#no-unbooked-appointments').removeClass('hidden');
                        }
                    }, 2000);
                };

                $.post('/appointments/delete/' + $this.data('id'))
                    .done(function deleteAppointmentSuccess(data, textStatus, jqXHR) {
                        appointmentDeleted();
                    })
                    .fail(function deleteAppointmentFailed(jqXHR, textStatus, errorThrown) {
                        switch (jqXHR.status) {
                            case 404:
                                appointmentDeleted();
                                break;

                            default:
                                $parent.append($newSpan.addClass(somethingHappenedClass).text('Something happened, try again!'));
                                break;
                        }
                    });
            });
        }
    },
    coach: {
        initialize: function () {
            arivale.global.initialize();

            arivale.helpers.setUpCancelUpcomingAvailabilityButton($('#upcoming-availability button'));

            var $addAvailabilityControl = $('#add-availability'),
                $errorMessage = $addAvailabilityControl.find('#error-message'),
                addAvailabilityChildren = $('.add-appointment').children();

            $addAvailabilityControl.find('button').click(function addAvailability() {
                if (!$errorMessage.hasClass('hidden')) {
                    $errorMessage.addClass('hidden');
                }

                var availabilityValues = [];
                $addAvailabilityControl.find('input').each(function () {
                    var val = $(this).val();
                    if (val && val.length > 0) {
                        availabilityValues.push(val);
                    }
                });

                if (availabilityValues.length === 2) {
                    var availabilityValuesStr = availabilityValues.join(' ');
                    $.post('/coach/availability/add/' + availabilityValuesStr)
                        .done(function availabilityAdded(data, textStatus, jqXHR) {
                            var $clonedTemplate = $($('#availability-added').html().replace('*#*id*#*', data.id).trim());
                            $clonedTemplate.find('span.display-text').text(data.display_text);

                            var $upcomingAvailability = arivale.helpers.addUpcomingAvailability($clonedTemplate);

                            setTimeout(function removeSuccessNotification() {
                                $upcomingAvailability.find('span.success-notification').remove();
                            }, 2000);

                            $errorMessage.find('span:first').html('');

                            $addAvailabilityControl.height($(addAvailabilityChildren[0]).height() + $(addAvailabilityChildren[1]).height());
                        })
                        .fail(function availabilityAddFailed(jqXHR, textStatus, errorThrown) {
                            switch (jqXHR.status) {
                                case 409:
                                    var errorMessageText = [
                                        "You already have a slot allocated that conflicts with the attempted time above.",
                                        "Please either cancel the existing slot or pick a new time."].join('<br/>');

                                    $errorMessage.find('span:first').html(errorMessageText);
                                    $errorMessage.removeClass('hidden');

                                    $addAvailabilityControl.height($(addAvailabilityChildren[0]).height() + $(addAvailabilityChildren[1]).height());
                                    break;

                                default:
                                    break;
                            }
                        });
                }
            });

            $('#booked-availability button').click(function cancelBookedAppointment() {
                var $this = $(this),
                    $parent = $this.parent(),
                    $newSpan = $('<span />'),
                    somethingHappenedClass = 'something-happened';

                $parent.find('span.' + somethingHappenedClass).remove();

                var appointmentCanceled = function () {
                    var $clonedParent = $parent.clone().removeClass('booked-appointment').addClass('upcoming-appointment');
                    $clonedParent.find('button').text('Delete');

                    arivale.helpers.addUpcomingAvailability($clonedParent);

                    $parent.siblings().remove();

                    $parent.html($newSpan.text('Appointment canceled.').html());
                    setTimeout(function removeText() {
                        $parent.remove();
                        if ($('.booked-appointment').length === 0) {
                            $('#no-booked-appointments').removeClass('hidden');
                        }
                    }, 2000);
                };

                $.post('/appointments/cancel/' + $this.data('id'))
                    .done(function clientSuccessfullyAdded(data, textStatus, jqXHR) {
                        appointmentCanceled();
                    })
                    .fail(function clientAddFailed(jqXHR, textStatus, errorThrown) {
                        switch (jqXHR.status) {
                            case 404:
                                appointmentCanceled();
                                break;

                            default:
                                $parent.append($newSpan.addClass(somethingHappenedClass).text('Something happened, try again!'));
                                break;
                        }
                    });
            });

            $('#potential-clients button').click(function addToClientele() {
                var $this = $(this),
                    $parent = $this.parent(),
                    $newSpan = $('<span />'),
                    somethingHappenedClass = 'something-happened';

                $parent.find('span.' + somethingHappenedClass).remove();

                $.post('/coach/clients/add/' + $this.data('clientId'))
                    .done(function clientSuccessfullyAdded(data, textStatus, jqXHR) {
                        $this.remove();

                        var $noExistingClients = $('#no-existing-clients');
                        if (!$noExistingClients.hasClass('hidden')) {
                            $noExistingClients.addClass('hidden');
                        }

                        $('#existing-clients').append($parent);
                    })
                    .fail(function clientAddFailed(jqXHR, textStatus, errorThrown) {
                        switch (jqXHR.status) {
                            case 409:
                                $this.replaceWith($newSpan.text('Looks like someone beat you to it...'));
                                break;

                            default:
                                $parent.append($newSpan.addClass(somethingHappenedClass).text('Something happened, try again!'));
                                break;
                        }
                    });
            });
        }
    },
    customer: {
        initialize: function () {
            arivale.global.initialize();

            arivale.customer._setUpCancelBookedAppointmentButtons($('#booked-availability button'));

            var $bookAppointmentControl = $('#book-appointment-control');
            $bookAppointmentControl.find('button').click(function bookAppointment() {
                var $selected = $bookAppointmentControl.find('select :selected');
                $.post('/appointments/book/' + $selected.val())
                    .done(function appointmentSuccessfullyBooked(data, textStatus, jqXHR) {
                        var $clonedTemplate = $($('#booking-added').html().replace('*#*id*#*', data.id).trim());
                        $clonedTemplate.find('span.display-text').text(data.display_text);

                        var $bookedAvailability = $('#booked-availability');

                        arivale.customer._setUpCancelBookedAppointmentButtons($clonedTemplate.find('button'));

                        var $noBookedAppointments = $bookedAvailability.find('#no-booked-appointments:first');
                        if (!$noBookedAppointments.hasClass('hidden')) {
                            $noBookedAppointments.addClass('hidden');
                        }

                        arivale.helpers.addTimeSlotInOrder($bookedAvailability, '.booked-appointment', $clonedTemplate, '.display-text');

                        $selected.remove()

                        var $coachHasAvailability = $('#coach-has-availability');
                        if ($coachHasAvailability.find('select option').length === 0) {
                            $coachHasAvailability.addClass('hidden');
                            $('#no-coach-availability').removeClass('hidden');
                        }

                        setTimeout(function removeSuccessNotification() { $bookedAvailability.find('span.success-notification').remove(); }, 2000);
                    })
                    .fail(function bookAppointmentFailed(jqXHR, textStatus, errorThrown) {
                        switch (jqXHR.status) {
                            case 404:
                                break;

                            default:
                                break;
                        }
                    });
            });
        },
        _setUpCancelBookedAppointmentButtons: function ($obj) {
            $obj.click(function cancelBookedAppointment() {
                var $this = $(this),
                    $parent = $this.parent(),
                    $newSpan = $('<span />'),
                    somethingHappenedClass = 'something-happened';

                $parent.find('span.' + somethingHappenedClass).remove();

                var appointmentCanceled = function () {
                    var $addedOption = $('<option>').text($parent.find('.display-text').text()).val($parent.find('button').data('id')),
                        $coachHasAvailability = $('#coach-has-availability'),
                        $coachHasAvailabilitySelect = $coachHasAvailability.find('select:first');

                    $parent.html($newSpan.text('Appointment canceled.').html());

                    setTimeout(function removeText() {
                        $parent.remove();
                        if ($('.booked-appointment').length === 0) {
                            $('#no-booked-appointments').removeClass('hidden');
                        }
                    }, 2000);

                    arivale.helpers.addTimeSlotInOrder($coachHasAvailabilitySelect, 'option', $addedOption);

                    if ($coachHasAvailability.hasClass('hidden')) {
                        $('#no-coach-availability').addClass('hidden');
                        $coachHasAvailability.removeClass('hidden');
                    }
                };

                $.post('/appointments/cancel/' + $this.data('id'))
                    .done(function appointmentSuccessfullyCanceled(data, textStatus, jqXHR) {
                        appointmentCanceled();
                    })
                    .fail(function clientAddFailed(jqXHR, textStatus, errorThrown) {
                        switch (jqXHR.status) {
                            case 404:
                                appointmentCanceled();
                                break;

                            default:
                                $parent.append($newSpan.addClass(somethingHappenedClass).text('Something happened, try again!'));
                                break;
                        }
                    });
            });
        }
    }
}